from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from horizon import tables

from nectar_dashboard.rcallocation import models


# Actions
class EditRequest(tables.LinkAction):
    name = "edit"
    verbose_name = ("Edit request")
    url = "horizon:allocation:requests:edit_request"
    classes = ("btn-associate",)

    def allowed(self, request, instance):
        return instance.can_be_edited()


class ViewHistory(tables.LinkAction):
    name = "view_history"
    verbose_name = "View history"
    url = "horizon:allocation:requests:allocation_history"


def status_icon(allocation):
    css_style = 'alloc-icon-wip'
    title = allocation.get_status_display()
    text = allocation.status
    if allocation.status == models.AllocationRequest.APPROVED:
        css_style = 'alloc-icon-ok'
    data = mark_safe('<p'
                     ' title="%s"'
                     ' class="alloc-icon %s">'
                     '<strong>%s</strong></p>'
                     % (title, css_style, text))
    return data


def allocation_title(allocation,
                     link='horizon:allocation:requests:allocation_view'):
    url = reverse(link, args=(allocation.pk,))
    # Escape the data inside while allowing our HTML to render
    data = mark_safe('<a href="%s">%s</a>'
                     '<br/>'
                     '<small class="muted">%s</small>' %
                     (escape(url),
                      escape(allocation.project_name),
                      escape(allocation.project_description)))
    return data


class BaseAllocationListTable(tables.DataTable):
    status = tables.Column(status_icon,
                           classes=['text-center'],
                           verbose_name="State")
    project = tables.Column(allocation_title,
                            verbose_name="Name", )
    associated_site = tables.Column('associated_site',
                                    verbose_name='Current Associated Site')
    national = tables.Column('national',
                             verbose_name='National')
    approver = tables.Column('approver_email',
                             verbose_name='Approver')
    contact = tables.Column("contact_email", verbose_name="Contact")
    modified_time = tables.Column("modified_time",
                                  verbose_name="Last Updated",
                                  filters=[lambda d: d.date()])
    end_date = tables.Column("end_date",
                             verbose_name="Expiry Date")

    class Meta:
        verbose_name = "Requests"
        table_actions = (tables.NameFilterAction,)
        row_actions = (EditRequest, ViewHistory,)


def delta_quota(allocation, want, have):
    if allocation.status in ('X', 'J'):
        return "%+d" % (int(want) - int(have))
    elif allocation.status == 'A':
        return have or '-'
    elif allocation.status in ('E', 'R'):
        return want or '-'
    return "Requested %s, currently have %s" % (want, have)


def get_quota(wanted, actual=None):
    def quota(allocation):
        want = getattr(allocation, wanted)
        have = getattr(allocation, actual, want)
        return delta_quota(allocation, want, have)
    return quota


def get_quota_by_resource(service, resource):
    def quota(allocation):
        want = 0
        have = 0
        for quota in \
            models.Quota.objects.filter(group__allocation=allocation,
                                        resource__service_type=service,
                                        resource__quota_name=resource):
            want += quota.requested_quota
            have += quota.quota
        return delta_quota(allocation, want, have)
    return quota


class AllocationHistoryTable(tables.DataTable):
    project = tables.Column("project_description", verbose_name="Project name",
                            link="horizon:allocation:requests:allocation_view")
    approver = tables.Column("approver_email", verbose_name="Approver")
    service_units = tables.Column(
        get_quota_by_resource("rating", "budget"),
        verbose_name="SUs")
    cores = tables.Column(
        get_quota_by_resource("compute", "cores"),
        verbose_name="Cores")
    ram = tables.Column(
        get_quota_by_resource("compute", "ram"),
        verbose_name="RAM")
    object_store = tables.Column(
        get_quota_by_resource("object", "object"),
        verbose_name="Object Storage")
    volume_storage = tables.Column(
        get_quota_by_resource("volume", "gigabytes"),
        verbose_name="Volume Storage")
    status = tables.Column("get_status_display", verbose_name="Status")
    modified_time = tables.Column(
        "modified_time", verbose_name="Modification time")

    class Meta:
        verbose_name = "Request History"
