from functools import partial

from horizon import tables as horizon_tables

from nectar_dashboard.rcallocation import tables


class UserAmendRequest(horizon_tables.LinkAction):
    name = "amend"
    verbose_name = "Amend/Extend allocation"
    url = "horizon:allocation:user_requests:edit_change_request"
    classes = ("btn-associate",)

    def allowed(self, request, instance):
        return instance.can_be_amended()


class UserEditRequest(tables.EditRequest):
    name = "user_edit"
    verbose_name = "Edit request"
    url = "horizon:allocation:user_requests:edit_request"

    def allowed(self, request, instance):
        return instance.can_user_edit()


class UserEditChangeRequest(tables.EditRequest):
    name = "user_edit_change"
    verbose_name = "Edit amend/extend request"
    url = "horizon:allocation:user_requests:edit_change_request"

    def allowed(self, request, instance):
        return instance.can_user_edit_amendment()


class CreateAllocation(horizon_tables.LinkAction):
    name = "create"
    verbose_name = "Request a new allocation"
    url = "horizon:allocation:request:request"
    icon = "plus"


class UserAllocationListTable(tables.BaseAllocationListTable):
    view_url = "horizon:allocation:user_requests:allocation_view"

    class Meta(tables.BaseAllocationListTable.Meta):
        row_actions = (
            UserEditRequest,
            UserAmendRequest,
            UserEditChangeRequest,
        )
        table_actions = (CreateAllocation,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columns['project'].transform = partial(
            self.columns['project'].transform, link=self.view_url
        )
        self.columns.pop('approver')
