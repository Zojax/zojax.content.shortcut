##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
import cgi
from transaction import abort
from zope import interface, component
from zope.event import notify
from zope.size.interfaces import ISized
from zope.proxy import removeAllProxies
from zope.security import canWrite, checkPermission
from zope.exceptions import DuplicationError
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.traversing.api import traverse, getPath, joinPath, getName
from zope.traversing.browser import absoluteURL
from zope.traversing.interfaces import TraversalError
from zope.security.interfaces import Unauthorized
from zope.security.proxy import removeSecurityProxy
from zope.annotation.interfaces import IAnnotations
from zope.dublincore.interfaces import ICMFDublinCore
from zope.copypastemove.interfaces import IPrincipalClipboard
from zope.copypastemove.interfaces import IContainerItemRenamer
from zope.copypastemove.interfaces import IObjectCopier, IObjectMover
from zope.app.container.interfaces import DuplicateIDError, IContainerNamesContainer
from zope.app.container.contained import notifyContainerModified
from zope.i18n import translate
from zope.lifecycleevent import ObjectModifiedEvent, Attributes

from zojax.table.table import Table
from zojax.table.column import Column, AttributeColumn
from zojax.table.interfaces import IColumn, IDataset, ITableConfiguration

from zojax.formatter.utils import getFormatter
from zojax.layoutform.interfaces import IFormWrapper
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.content.type.interfaces import IItem, IOrder
from zojax.content.type.interfaces import IReordable, IContentType
from zojax.content.type.interfaces import IContentViewView, IRenameNotAllowed
from zojax.content.type.interfaces import IContentContainer, IUnremoveableContent
from zojax.content.type.interfaces import IContainerContentsTable

from interfaces import _
from interfaces import IContainerListing, IContainerURL, IRenameContainerContents


class ContainerListing(Table):
    interface.implements(IContainerListing)

    title = _('Content listing')

    msgEmptyTable = _(u'There are no items in this container.')

    pageSize = 20
    enabledColumns = ('icon', 'name', 'title', 'created', 'modified')
    disabledColumns = ()

    def initDataset(self):
        order = IOrder(self.context, None)
        if order is not None:
            contents = order.keys()
            self.container = order
        else:
            contents = self.context.keys()
            self.container = self.context
        self.dataset = removeSecurityProxy(contents)

    def update(self):
        super(ContainerListing, self).update()

        request = self.request

        url = getMultiAdapter((self.context, self), IContainerURL)
        self.environ['url'] = url.absoluteURL()

        self.environ['formatter'] = getFormatter(
            request, 'fancyDatetime', 'short')

    def records(self):
        if self.batch is not None:
            for content in self.batch:
                yield self.RecordClass(self, self.container[content])
        else:
            for content in self.dataset:
                yield self.RecordClass(self, self.container[content])

    def updateContent(self, content, environ):
        url = self.environ['url']

        environ['url'] = None
        environ['viewUrl'] = None

        if url:
            environ['url'] = '%s/%s'%(self.environ['url'], content.__name__)

            viewName = component.queryMultiAdapter(
                (content, self.request), IContentViewView)
            if viewName:
                environ['viewUrl'] = '%s/%s'%(environ['url'], viewName.name)
            else:
                environ['viewUrl'] = '%s/'%environ['url']


class ContainerContents(ContainerListing):
    interface.implements(IContainerContentsTable)

    enabledColumns = ('id', 'icon', 'name',
                      'title', 'size', 'created', 'modified')

    updated = False

    supportsCut = False
    supportsCopy = False
    supportsRename = False
    supportsDelete = False

    def initColumns(self):
        super(ContainerContents, self).initColumns()

        hasId = False

        for column in self.columns:
            if column.name == 'id':
                return

        column = component.getMultiAdapter(
            (self.context, self.request, self), IColumn, name='id')
        column.update()

        self.columns = [column] + list(self.columns)

    def isWrapped(self):
        context = self.view

        while 1:
            if IFormWrapper.providedBy(context):
                return True

            context = getattr(context, '__parent__', None)
            if context is None:
                return False

    def update(self):
        if self.updated:
            return

        context = self.context
        request = self.request

        if 'form.buttons.apply' in request:
            self.environ['applyButton'] = True

        elif 'form.buttons.rename' in request:
            if not request.get("ids"):
                IStatusMessage(request).add(
                    _("You didn't specify any ids to rename."), 'warning')
            else:
                interface.alsoProvides(self, IRenameContainerContents)

        elif "form.buttons.delete" in request:
            self.removeObjects()

        elif "form.buttons.copy" in request:
            self.copyObjects()

        elif "form.buttons.cut" in request:
            self.cutObjects()

        elif "form.buttons.paste" in request:
            self.pasteObjects()

        order = IOrder(self.context, None)
        if order is not None and IReordable.providedBy(order):
            self.orderButtons = len(order) > 1

            changed = False
            selected = request.get('ids', [])

            if 'form.buttons.moveup' in request:
                changed = order.moveUp(selected)

            elif 'form.buttons.movetop' in request:
                changed = order.moveTop(selected)

            elif 'form.buttons.movedown' in request:
                changed = order.moveDown(selected)

            elif 'form.buttons.movebottom' in request:
                changed = order.moveBottom(selected)

            if changed:
                notifyContainerModified(self.context)
                IStatusMessage(request).add(
                    _(u'Items order have been changed.'))
        else:
            self.orderButtons = False

        super(ContainerContents, self).update()

        self.setupButtons()

        self.updated = True

    def setupButtons(self):
        self.specialButtons = IRenameContainerContents.providedBy(self)
        self.normalButtons = not self.specialButtons
        self.supportsPaste = self.pasteable()

    def safe_getattr(self, obj, attr, default):
        """Attempts to read the attr, returning default if Unauthorized."""
        try:
            return getattr(obj, attr, default)
        except Unauthorized:
            return default

    def removeObjects(self):
        """Remove objects specified in a list of object ids"""
        request = self.request
        ids = request.get('ids')
        if not ids:
            IStatusMessage(request).add(
                _("You didn't specify any ids to remove."), 'error')
            return

        container = self.context
        deleted = False
        for id in ids:
            if not IUnremoveableContent.providedBy(container[id]):
                del container[id]
                deleted = True
        if deleted:
            IStatusMessage(request).add(
                _('Selected items has been removed.'))
        else:
            IStatusMessage(request).add(
                _('No items can be removed.'))

    def copyObjects(self):
        """Copy objects specified in a list of object ids"""
        request = self.request
        ids = request.get('ids')
        if not ids:
            IStatusMessage(request).add(
                _("You didn't specify any ids to copy."), 'error')
            return

        container = self.context
        container_path = getPath(container)

        items = []
        for id in ids:
            ob = container[id]
            copier = IObjectCopier(ob)
            if not copier.copyable():
                IStatusMessage(request).add(
                    _("Object '${name}' cannot be copied",{"name": id}),'error')
                return
            items.append(joinPath(container_path, id))

        # store the requested operation in the principal annotations:
        clipboard = getPrincipalClipboard(request)
        clipboard.clearContents()
        clipboard.addItems('copy', items)

        IStatusMessage(request).add(_('Selected items has been copied.'))

    def cutObjects(self):
        """move objects specified in a list of object ids"""
        request = self.request
        ids = request.get('ids')
        if not ids:
            IStatusMessage(request).add(
                _("You didn't specify any ids to cut."), 'error')
            return

        container = self.context
        container_path = getPath(container)

        items = []
        for id in ids:
            ob = container[id]
            mover = IObjectMover(ob)
            if not mover.moveable():
                IStatusMessage(request).add(
                    _("Object '${name}' cannot be moved",{"name": id}),'error')
                return
            items.append(joinPath(container_path, id))

        # store the requested operation in the principal annotations:
        clipboard = getPrincipalClipboard(request)
        clipboard.clearContents()
        clipboard.addItems('cut', items)

        IStatusMessage(request).add(_('Selected items has been cut.'))

    def pasteable(self):
        """Decide if there is anything to paste """
        target = self.context
        clipboard = getPrincipalClipboard(self.request)
        items = clipboard.getContents()
        for item in items:
            try:
                obj = traverse(target, item['target'])
            except TraversalError:
                pass
            else:
                if item['action'] == 'cut':
                    mover = IObjectMover(obj)
                    moveableTo = self.safe_getattr(mover, 'moveableTo', None)
                    if moveableTo is None or not moveableTo(target):
                        return False
                elif item['action'] == 'copy':
                    copier = IObjectCopier(obj)
                    copyableTo = self.safe_getattr(copier, 'copyableTo', None)
                    if copyableTo is None or not copyableTo(target):
                        return False
                else:
                    raise

        return True

    def pasteObjects(self):
        """Paste ojects in the user clipboard to the container """
        target = self.context
        clipboard = getPrincipalClipboard(self.request)
        items = clipboard.getContents()
        moved = False
        not_pasteable_ids = []
        for item in items:
            duplicated_id = False
            try:
                obj = traverse(target, item['target'])
            except TraversalError:
                pass
            else:
                if item['action'] == 'cut':
                    mover = IObjectMover(removeAllProxies(obj))
                    try:
                        mover.moveTo(target)
                        moved = True
                    except DuplicateIDError:
                        duplicated_id = True
                elif item['action'] == 'copy':
                    copier = IObjectCopier(removeAllProxies(obj))
                    try:
                        copier.copyTo(target)
                    except DuplicateIDError:
                        duplicated_id = True
                else:
                    raise

            if duplicated_id:
                not_pasteable_ids.append(getName(obj))

        if moved:
            clipboard.clearContents()

        if not_pasteable_ids:
            abort()
            IStatusMessage(request).add(
                _("The given name(s) %s is / are already being used" %(
                str(not_pasteable_ids))), 'error')

    def hasClipboardContents(self):
        """Interogate the ``PrinicipalAnnotation`` to see if clipboard
        contents exist."""
        if not self.supportsPaste:
            return False

        # touch at least one item to in clipboard confirm contents
        clipboard = getPrincipalClipboard(self.request)
        items = clipboard.getContents()
        for item in items:
            try:
                traverse(self.context, item['target'])
            except TraversalError:
                pass
            else:
                return True

        return False


def getPrincipalClipboard(request):
    """Return the clipboard based on the request."""
    user = request.principal
    annotations = IAnnotations(user)
    return IPrincipalClipboard(annotations)


class ContainerURL(object):
    interface.implements(IContainerURL)
    component.adapts(interface.Interface, IContainerListing)

    def __init__(self, context, table):
        self.context = context
        self.table = table

    def absoluteURL(self):
        try:
            return absoluteURL(self.context, self.table.request)
        except TypeError:
            return None


class IdColumn(AttributeColumn):
    component.adapts(
        IContentContainer, interface.Interface, IContainerContentsTable)

    weight = 0
    name = 'id'
    attrName = '__name__'
    cssClass = 'z-table-cell-min'

    def update(self):
        super(IdColumn, self).update()

        self.table.environ['activeIds'] = self.request.get('ids', ())

    def __bind__(self, content, globalenviron, environ):
        clone = super(IdColumn, self).__bind__(content, globalenviron, environ)

        table = self.table

        copier = IObjectCopier(content, None)
        if copier is not None and copier.copyable():
            copyable = True
            table.supportsCopy = True
        else:
            copyable = False

        moveable = False
        renameable = False
        deletable = False

        if not IUnremoveableContent.providedBy(content):
            mover = IObjectMover(content, None)
            if mover is not None and mover.moveable():
                moveable = True
                table.supportsCut = True

                if not IRenameNotAllowed.providedBy(content):
                    renameable = \
                        not IContainerNamesContainer.providedBy(self.context)

                    if renameable:
                        table.supportsRename = True

        if not IUnremoveableContent.providedBy(content) and \
                checkPermission('zojax.DeleteContent', content):
            deletable = True
            table.supportsDelete = True

        clone.buttons = copyable or moveable or renameable or deletable

        return clone

    def render(self):
        if not self.buttons:
            return u''

        value = self.query()
        ids = self.globalenviron['activeIds']
        return u'<input type="checkbox" name="ids:list" value="%s" %s/>'%(
            cgi.escape(value), value in ids and u'checked="yes"' or u'')


class RenameIdColumn(IdColumn):
    component.adapts(IContentContainer,
                     interface.Interface, IRenameContainerContents)

    def render(self):
        value = self.query()
        if value in self.globalenviron['activeIds']:
            return u'<input type="hidden" name="ids:list" value="%s" />'%\
                   cgi.escape(value)
        else:
            return ''


class IconColumn(Column):
    component.adapts(IContentContainer, interface.Interface, IContainerListing)

    weight = 5
    name = 'icon'
    cssClass = 'z-table-cell-min'

    def query(self, default=''):
        return queryMultiAdapter((self.content, self.request), name='zmi_icon')

    def render(self):
        zmi_icon = self.query()
        if zmi_icon is None:
            return ''
        else:
            return zmi_icon()


class NameColumn(AttributeColumn):
    component.adapts(IContentContainer, interface.Interface, IContainerListing)

    name = 'name'
    title = _('Name')

    weight = 10
    attrName = '__name__'

    def render(self):
        value = cgi.escape(self.query())
        if self.environ['viewUrl']:
            return u'<a href="%s">%s</a>'%(self.environ['viewUrl'], value)
        else:
            return value


class ContentsNameColumn(NameColumn):
    component.adapts(
        IContentContainer, interface.Interface, IContainerContentsTable)

    def update(self):
        super(ContentsNameColumn, self).update()

        # Given a sequence of tuples of old, new ids we rename
        if 'applyButton' in self.table.environ:
            ids = self.table.environ['activeIds']
            newids = self.request.get("newIds", ())

            renamed = False
            renamer = IContainerItemRenamer(self.table.context)
            for oldid, newid in zip(ids, newids):
                if newid != oldid:
                    try:
                        renamer.renameItem(oldid, newid)
                    except DuplicationError:
                        IStatusMessage(self.request).add(
                            _('Item with this name already exists.'), 'error')
                        return

                    renamed = True
                    ids[ids.index(oldid)] = newid

            if renamed:
                IStatusMessage(self.request).add(_('Items have been renamed.'))

    def render(self):
        request = self.request
        content = self.content
        value = cgi.escape(self.query() or '')

        if self.environ['url']:
            if checkPermission('zojax.ModifyContent', content):
                return u'<a href="%s/context.html">%s</a>'%(
                    self.environ['url'], value)
            else:
                viewName = queryMultiAdapter((content, request), IContentViewView)
                if viewName:
                    return u'<a href="%s/%s">%s</a>'%(
                        self.environ['url'], viewName.name, value)
                else:
                    return u'<a href="%s/">%s</a>'%(self.environ['url'], value)
        else:
            return value


class RenameNameColumn(ContentsNameColumn):
    component.adapts(IContentContainer,
                     interface.Interface, IRenameContainerContents)

    def render(self):
        if IUnremoveableContent.providedBy(self.content):
            return super(RenameNameColumn, self).render()

        value = self.query()
        if value in self.globalenviron['activeIds']:
            return u'<input type="text" name="newIds:list" '\
                   'size="10" value="%s" />'%cgi.escape(value)
        else:
            return super(RenameNameColumn, self).render()


class TitleColumn(Column):
    component.adapts(IContentContainer, interface.Interface, IContainerListing)

    name = 'title'
    title = _('Title')

    weight = 20

    def query(self, default=None):
        content = self.content
        item = IItem(content, None)

        title = None
        if item is not None:
            title = cgi.escape(item.title or u'')
        else:
            try:
                title = getattr(ICMFDublinCore(content, None), 'title', None)
            except:
                pass

        return title or _('[No title]')


class ContentsTitleColumn(TitleColumn):
    component.adapts(
        IContentContainer, interface.Interface, IContainerContentsTable)

    def update(self):
        super(ContentsTitleColumn, self).update()

        # Given a sequence of tuples of old, new ids we rename
        if 'applyButton' in self.table.environ:
            ids = self.table.environ['activeIds']
            newtitles = self.request.get("newTitles", ())

            for id, title in zip(ids, newtitles):
                item = self.table.context[id]
                item = IItem(item)
                item.title = title
                notify(ObjectModifiedEvent(item, Attributes(IItem, 'title')))
            IStatusMessage(self.request).add(_('Items have been retitled.'))


class RenameTitleColumn(TitleColumn):
    component.adapts(IContentContainer,
                     interface.Interface, IRenameContainerContents)

    def render(self):
        content = self.content

        if content.__name__ not in self.globalenviron['activeIds']:
            return super(RenameTitleColumn, self).render()

        if IItem.providedBy(content):
            if not canWrite(content, 'title'):
                return super(RenameTitleColumn, self).render()
        else:
            dc= ICMFDublinCore(content, None)
            if dc is not None:
                if not canWrite(dc, 'title'):
                    return super(RenameTitleColumn, self).render()

        return u'<input type="text" name="newTitles:list" '\
               'size="14" value="%s" />'%cgi.escape(self.query())


class TypeColumn(Column):
    component.adapts(
        IContentContainer, interface.Interface, IContainerContentsTable)

    name = 'type'
    title = _('Type')

    weight = 25

    def query(self, default=None):
        ct = IContentType(self.content, None)
        if ct is not None:
            return ct.title
        else:
            return ''


class SizeColumn(Column):
    component.adapts(
        IContentContainer, interface.Interface, IContainerContentsTable)

    name = 'size'
    title = _('Size')

    weight = 30

    def query(self, default=None):
        return ISized(self.content, None)

    def render(self):
        value = self.query()

        if value:
            return translate(value.sizeForDisplay())
        else:
            return u''


class CreatedColumn(Column):
    component.adapts(IContentContainer, interface.Interface, IContainerListing)

    name = 'created'
    title = _('Created')

    weight = 40

    def query(self, default=None):
        dc = ICMFDublinCore(self.content, None)
        if dc is not None:
            return dc.created

        return None

    def render(self):
        value = self.query()
        if value:
            return self.globalenviron['formatter'].format(value)

        return value


class ModifiedColumn(Column):
    component.adapts(IContentContainer, interface.Interface, IContainerListing)

    name = 'modified'
    title = _('Modified')

    weight = 50

    def query(self, default=None):
        dc = ICMFDublinCore(self.content, None)
        if dc is not None:
            return dc.modified

        return None

    def render(self):
        value = self.query()
        if value:
            return self.globalenviron['formatter'].format(value)

        return '---'
