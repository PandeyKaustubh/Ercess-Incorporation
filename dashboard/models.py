# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from datetime import datetime
from django.utils import timezone

class ErcesscorpBlogdata(models.Model):
    blog_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.CharField(max_length=100)
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Ercesscorp_blogdata'


class ErcesscorpContactdata(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=70)
    mobile = models.BigIntegerField()
    purpose = models.CharField(max_length=20)
    comment = models.CharField(max_length=1000)

    class Meta:
        managed = False
        db_table = 'Ercesscorp_contactdata'


class ErcesscorpRegistrationdata(models.Model):
    gender = models.CharField(max_length=10)
    location = models.CharField(max_length=30)
    submitted = models.IntegerField()
    how_u_know = models.CharField(max_length=100)
    verify = models.IntegerField()
    user = models.ForeignKey('AuthUser', models.DO_NOTHING, unique=True)

    class Meta:
        managed = False
        db_table = 'Ercesscorp_registrationdata'


class ErcesscorpUserregistrationtoken(models.Model):
    user_email_token = models.CharField(max_length=250)
    user_email_token_created_on = models.DateTimeField(blank=True, null=True)
    user_password_token = models.CharField(max_length=250)
    user_email = models.CharField(max_length=250)
    user_password_token_created_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Ercesscorp_userregistrationtoken'


class AboutCountries(models.Model):
    table_id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=50)
    country_code = models.CharField(max_length=2)
    currency = models.CharField(max_length=10)
    pincode_size = models.IntegerField()
    event_advertising = models.CharField(max_length=11)
    event_stall_spaces = models.CharField(max_length=11)
    event_mcp = models.CharField(max_length=11)
    timezone = models.CharField(max_length=255, blank=True, null=True)
    currency_code = models.CharField(max_length=255, blank=True, null=True)
    bank_regex1 = models.CharField(max_length=100, blank=True, null=True)
    bank_regex2 = models.CharField(max_length=100, blank=True, null=True)
    default_sms_credits = models.IntegerField()
    default_email_credits = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'about_countries'


class Admin(models.Model):
    table_id = models.AutoField(primary_key=True)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    email_id = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    admin_type = models.IntegerField()
    admin_active = models.IntegerField()
    team = models.IntegerField()
    mobile = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'admin'


class AdminAccessTypes(models.Model):
    table_id = models.AutoField(primary_key=True)
    updated_on = models.DateTimeField()
    parameter = models.CharField(max_length=110)
    details = models.TextField()

    class Meta:
        managed = False
        db_table = 'admin_access_types'


class AdminAccesses(models.Model):
    access_id = models.AutoField(primary_key=True)
    admin_id = models.IntegerField()
    updated_on = models.DateTimeField()
    access_type = models.IntegerField()
    read_access = models.IntegerField()
    write_access = models.IntegerField()
    delete_access = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'admin_accesses'


class AdminActionLog(models.Model):
    table_id = models.AutoField(primary_key=True)
    admin_id = models.IntegerField()
    timestamp = models.DateTimeField()
    parameter = models.CharField(max_length=150)
    event_id = models.IntegerField()
    action_taken = models.TextField()

    class Meta:
        managed = False
        db_table = 'admin_action_log'


class AdminEditorialLogs(models.Model):
    table_id = models.AutoField(primary_key=True)
    admin_id = models.IntegerField()
    event_id = models.IntegerField()
    timestamp = models.DateTimeField()
    data_type = models.TextField()
    old_data = models.TextField()
    new_data = models.TextField()

    class Meta:
        managed = False
        db_table = 'admin_editorial_logs'


class AdminEventAssignment(models.Model):
    table_id = models.AutoField(primary_key=True)
    admin_id = models.IntegerField()
    super_admin_id = models.IntegerField(blank=True, null=True)
    event_id = models.IntegerField()
    assignment_timestamp = models.DateTimeField()
    deadline = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin_event_assignment'


class AdminEventConcerns(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    message = models.TextField()
    date_added = models.DateTimeField()
    resolve = models.IntegerField()
    admin_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'admin_event_concerns'


class AdminPromotionPostings(models.Model):
    posting_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    admin_id = models.IntegerField()
    timestamp = models.DateTimeField()
    group_name = models.CharField(max_length=600)
    group_link = models.CharField(max_length=600)
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'admin_promotion_postings'


class AdminPromotionalContents(models.Model):
    content_id = models.AutoField(primary_key=True)
    admin_id = models.IntegerField()
    date_added = models.DateTimeField()
    event_id = models.IntegerField()
    contents = models.TextField()

    class Meta:
        managed = False
        db_table = 'admin_promotional_contents'


class AdminTaskManagement(models.Model):
    task_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    raised_by = models.IntegerField()
    raised_to = models.IntegerField()
    timestamp = models.DateTimeField()
    priority = models.CharField(max_length=25)
    message = models.TextField()
    status = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'admin_task_management'


class AdminsWrongSubmissions(models.Model):
    table_id = models.AutoField(primary_key=True)
    link_id = models.CharField(max_length=11)
    submitted_by = models.IntegerField()
    verified_by = models.IntegerField()
    date_added = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admins_wrong_submissions'


class Articles2(models.Model):
    country = models.CharField(max_length=45)
    event_name = models.CharField(max_length=200)
    md5 = models.CharField(max_length=35)
    date_added = models.DateTimeField(blank=True, null=True)
    profile_image = models.CharField(max_length=350)
    banner = models.CharField(max_length=350)
    editable_image = models.CharField(max_length=300, blank=True, null=True)
    sdate = models.DateTimeField(db_column='sDate', blank=True, null=True)  # Field name made lowercase.
    edate = models.DateTimeField(db_column='eDate', blank=True, null=True)  # Field name made lowercase.
    address_line1 = models.TextField(blank=True, null=True)
    address_line2 = models.TextField(blank=True, null=True)
    # @author Shubham
    pincode = models.CharField(max_length=10, null=True, default=0)
    # ends here ~ @author Shubham
    state = models.CharField(max_length=30)
    city = models.TextField()
    locality = models.CharField(max_length=50)
    full_address = models.CharField(max_length=350)
    latitude = models.CharField(max_length=150)
    longitude = models.CharField(max_length=150)
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField()
    website = models.CharField(max_length=500, blank=True, null=True)
    fb_page = models.CharField(max_length=200, blank=True, null=True)
    fb_event_page = models.CharField(max_length=200, blank=True, null=True)
    event_hashtag = models.CharField(max_length=30, blank=True, null=True)
    source_name = models.CharField(max_length=30)
    source_url = models.CharField(max_length=350)
    email_id_organizer = models.CharField(max_length=100)
    ticket_url = models.TextField()
    place_id = models.CharField(max_length=500)
    webinar_link = models.CharField(max_length=500, blank=True, null=True)
    # venue_not_decided = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'articles2'
        unique_together = (('event_name', 'sdate', 'edate', 'full_address'),)


class AttendeeAnnouncements(models.Model):
    event_id = models.IntegerField()
    org_id = models.IntegerField()
    msg = models.TextField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'attendee_announcements'


class AttendeeFormBuilder(models.Model):
    ques_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    ques_title = models.TextField()
    ques_type = models.IntegerField()
    ques_accessibility = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'attendee_form_builder'


class AttendeeFormOptions(models.Model):
    option_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    ques_id = models.IntegerField()
    option_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'attendee_form_options'


class AttendeeFormResponse(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    ticket_id = models.IntegerField()
    attendee_id = models.IntegerField()
    ques_id = models.IntegerField()
    booking_id = models.CharField(max_length=20)
    response = models.CharField(max_length=400)

    class Meta:
        managed = False
        db_table = 'attendee_form_response'


class AttendeeFormTypes(models.Model):
    type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'attendee_form_types'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.ForeignKey(AuthUser, models.DO_NOTHING, unique=True)

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class BankDetails(models.Model):
    user_id = models.IntegerField()
    bank_name = models.CharField(max_length=20)
    ac_holder_name = models.CharField(max_length=70)
    ac_type = models.CharField(max_length=15)
    ac_number = models.CharField(max_length=26)
    ifsc_code = models.CharField(max_length=14)
    branch = models.CharField(max_length=30)
    gst_number = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'bank_details'


class Blogs(models.Model):
    blog_id = models.AutoField(primary_key=True)
    date_added = models.DateTimeField()
    added_by = models.CharField(max_length=50)
    title = models.CharField(max_length=120)
    blog_img = models.CharField(max_length=300)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'blogs'


class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=38)
    page_name = models.CharField(max_length=30)
    short_lived = models.IntegerField()
    country = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'categories'


class CategorizedEvents(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    category_id = models.IntegerField()
    topic_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categorized_events'


class CitiesList(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.TextField()
    state = models.TextField()
    country = models.TextField()
    major = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cities_list'


class CustomerSupport(models.Model):
    table_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    complaint_id = models.CharField(max_length=14)
    subject = models.TextField()
    thread_status = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'customer_support'


class CustomerSupportThreads(models.Model):
    table_id = models.AutoField(primary_key=True)
    complaint_id = models.CharField(max_length=12)
    complaint_body = models.TextField()
    complaint_date = models.DateTimeField()
    admin_response = models.TextField()
    admin_response_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer_support_threads'


class DiscountErcess(models.Model):
    table_id = models.AutoField(primary_key=True)
    coupon = models.CharField(max_length=20)
    amount = models.CharField(max_length=10)
    amount_type = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    explanation = models.TextField()

    class Meta:
        managed = False
        db_table = 'discount_ercess'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class ErcessIndiaeveStates(models.Model):
    table_id = models.AutoField(primary_key=True)
    state_name = models.CharField(max_length=50)
    state_id = models.IntegerField()
    site_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ercess_indiaeve_states'


class ErcessOtherMappings(models.Model):
    table_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    id = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=30)
    partner_id = models.IntegerField(blank=True, null=True)
    date_added = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ercess_other_mappings'


class ErcessPartnersCategories(models.Model):
    table_id = models.AutoField(primary_key=True)
    ercess_category = models.IntegerField()
    partner_category = models.CharField(max_length=50, blank=True, null=True)
    partner_category_id = models.IntegerField(blank=True, null=True)
    partner_id = models.CharField(db_column='partner_Id', max_length=50)  # Field name made lowercase.
    date_modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ercess_partners_categories'


class ErcessPartnersSubcategories(models.Model):
    subcat_id = models.AutoField(primary_key=True)
    ercess_topic_id = models.IntegerField()
    partner_subcate_name = models.CharField(max_length=40)
    partner_subcate_id = models.IntegerField(blank=True, null=True)
    partner_id = models.IntegerField()
    date_added = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ercess_partners_subcategories'


class EventEditLogs(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    last_updated = models.DateTimeField()
    parameter = models.CharField(max_length=100)
    taken_action = models.CharField(max_length=100)
    old_data = models.TextField()
    new_data = models.TextField()
    role = models.CharField(max_length=100)
    user_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'event_edit_logs'


class EventProcesses(models.Model):
    process_id = models.AutoField(primary_key=True)
    last_updated = models.DateTimeField()
    process_type = models.CharField(max_length=100)
    what_to_process = models.CharField(max_length=100)
    msg_to_org = models.TextField()
    active = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'event_processes'


class EventStatusOnChannel(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    last_updated = models.DateTimeField(blank=True, null=True)
    site_id = models.IntegerField()
    admin_id = models.IntegerField()
    link = models.CharField(max_length=300)
    promotion_status = models.CharField(max_length=50)
    partner_status = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'event_status_on_channel'


class EventVerificationResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    verified_at = models.DateTimeField()
    verified_against = models.CharField(max_length=100)
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'event_verification_result'


class FbEvents(models.Model):
    event_id = models.CharField(primary_key=True, max_length=100)
    country_name = models.TextField(blank=True, null=True)
    event_link = models.TextField(blank=True, null=True)
    heading = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fb_events'


class FbOrganizers(models.Model):
    evid = models.CharField(max_length=100, blank=True, null=True)
    organizer = models.TextField(db_column='Organizer', blank=True, null=True)  # Field name made lowercase.
    host_link = models.TextField(blank=True, null=True)
    email_id = models.TextField(blank=True, null=True)
    promotion_mail_status = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fb_organizers'


class FinanceSettlement(models.Model):
    finance_table_id = models.AutoField(primary_key=True)
    booking_id = models.CharField(max_length=100)
    sale_id = models.IntegerField()
    sold_on = models.CharField(max_length=100, blank=True, null=True)
    event_id = models.IntegerField()
    receive_date = models.DateTimeField(blank=True, null=True)
    receive_ref_num = models.CharField(max_length=100, blank=True, null=True)
    partner_conv_fee = models.CharField(max_length=100)
    partner_tax = models.CharField(max_length=100)
    amount_received = models.CharField(max_length=100)
    ercess_convenience = models.CharField(max_length=100)
    ercess_gst = models.CharField(max_length=100)
    payable_to_organizer = models.CharField(max_length=100)
    process_date = models.DateTimeField(blank=True, null=True)
    accountant_id = models.IntegerField()
    partner_invoice_id = models.CharField(max_length=100)
    ercess_invoice_id = models.IntegerField()
    partner_notes = models.TextField()
    organizer_notes = models.TextField()
    final_settlement = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'finance_settlement'
class BoostEvent(models.Model):
    id=models.AutoField(primary_key=True)
    event_id=models.IntegerField()
    city= models.CharField(max_length=500)
    class Meta:
        managed = False
        db_table = 'BoostEvent'

class FinanceStandardCharges(models.Model):
    charges_id = models.AutoField(primary_key=True)
    country_id = models.IntegerField()
    fee = models.CharField(max_length=11)
    fee_type = models.CharField(max_length=20)
    tax_name = models.CharField(max_length=2000)
    tax_value = models.CharField(max_length=2000)
    service_type = models.CharField(max_length=2000)
    service_details = models.CharField(max_length=2000)
    sms = models.IntegerField()
    email = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'finance_standard_charges'


class MessageTemplates(models.Model):
    message_id = models.AutoField(primary_key=True)
    used_for = models.CharField(max_length=30)
    explanation = models.TextField()
    subject = models.TextField()
    body = models.TextField()

    class Meta:
        managed = False
        db_table = 'message_templates'


class OrganizerAssets(models.Model):
    asset_id = models.AutoField(primary_key=True)
    admin_id = models.IntegerField()
    organizer_id = models.IntegerField()
    event_id = models.IntegerField()
    date_added = models.DateTimeField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    file = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'organizer_assets'


class PartnerCurrencies(models.Model):
    table_id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=30)
    date_added = models.DateTimeField()
    partner_id = models.IntegerField()
    currency_name = models.CharField(max_length=30)
    currency_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'partner_currencies'

class StatusOnChannel(models.Model):
    table_id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    last_updated = models.DateTimeField()
    site_id = models.IntegerField()
    admin_id = models.IntegerField()
    link = models.CharField(max_length=350)
    promotion_status = models.CharField(max_length=30)
    partner_status = models.CharField(max_length=30)
    #validation_status_sent = models.CharField(max_length=30,blank=True, null=True)

class PartnerSites(models.Model):
    table_id = models.AutoField(primary_key=True)
    site_name = models.CharField(max_length=150)
    site_url = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=50)
    website = models.IntegerField()
    app = models.IntegerField()
    site_use = models.CharField(max_length=250)
    coverage = models.CharField(max_length=250)
    method = models.CharField(max_length=20)
    doc_name = models.CharField(max_length=50)
    email1 = models.CharField(max_length=60)
    email2 = models.CharField(max_length=60)
    cc = models.CharField(max_length=60)
    restriction = models.CharField(max_length=500)
    support_name = models.CharField(max_length=60)
    support_email = models.CharField(max_length=60)
    support_mobile = models.CharField(max_length=40)
    payment_policy = models.CharField(max_length=250)
    payment_within_days = models.IntegerField()
    merchant_name = models.CharField(max_length=200)
    official_convenience_fee = models.CharField(max_length=20)
    official_transaction_fee = models.CharField(max_length=20)
    official_flat_charges = models.CharField(max_length=20)
    official_tax_charges = models.CharField(max_length=3)
    negotiated_convenience_fee = models.CharField(max_length=20)
    negotiated_transaction_fee = models.CharField(max_length=20)
    negotiated_flat_charges = models.CharField(max_length=20)
    negotiated_tax_charges = models.CharField(max_length=3)
    convenience_fee_organizer = models.CharField(max_length=11)
    transaction_fee_organizer = models.CharField(max_length=11)
    flat_fee_organizer = models.CharField(max_length=11)
    tax_fee_organizer = models.CharField(max_length=11)
    additional_msg = models.CharField(max_length=1000)
    active_state = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'partner_sites'


class PartnerTimezones(models.Model):
    timezone_id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=40)
    last_updated = models.DateTimeField()
    partner_id = models.IntegerField()
    timezone = models.CharField(max_length=50)
    partner_zone_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'partner_timezones'


class PasswordResetLogs(models.Model):
    user_id = models.IntegerField()
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'password_reset_logs'

# @author Shubham
class PaymentSettlement(models.Model):
    settlement_id = models.AutoField(primary_key=True)
    date_added = models.DateTimeField(null=False, default=datetime.now())
    date_modified = models.DateTimeField(null=False, default=datetime.now())
    booking_id = models.CharField(max_length=50, null=False, default='')
    ticket_sale_id = models.CharField(max_length=50, null=False, default='')
    added_by = models.CharField(max_length=11, null=False, default='')
    modified_by = models.CharField(max_length=11, null=False, default='')
    receival_status = models.CharField(max_length=50, null=False, default='pending')
    expected_amnt_partner = models.CharField(max_length=11, null=False, default='')
    rcvd_amnt_partner = models.CharField(max_length=11, null=False, default='')
    receival_date = models.DateTimeField(null=False, default=datetime.now())
    receival_invoice = models.CharField(max_length=300, null=False, default='')
    partner_dispute = models.TextField(null=False, default='')
    process_status = models.CharField(max_length=50, null=False, default='pending')
    amount_processed = models.CharField(max_length=11, null=False, default='')
    amount_process_date = models.DateTimeField(null=False, default=datetime.now())
    process_invoice = models.CharField(max_length=300, null=False, default='')
    organizer_dispute = models.TextField(null=False, default='')

    class Meta:
        managed = False
        db_table = 'payment_settlement'

# ends here ~ @author Shubham

class Rsvp(models.Model):
    table_id = models.AutoField(primary_key=True)
    date_added = models.DateTimeField(null=False, default=datetime.now())
    event_id = models.IntegerField(null=False, default=0)
    locked = models.IntegerField(null=False, default=0)
    supplied_by = models.CharField(max_length=30, null=False, default='')
    attendee_name = models.CharField(max_length=30, null=False, default='')
    attendee_email = models.CharField(max_length=80, null=False, default='')
    attendee_contact = models.CharField(max_length=12, null=False, default='')
    message = models.CharField(max_length=250, null=False, default='')

    class Meta:
        managed = False
        db_table = 'rsvp'

# if event_active = 2 (pause) , 3( Cancel it) ,4(sold out)
class StatusPromotionTicketing(models.Model):
    status_promotion_ticketing_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    unique_id = models.CharField(max_length=10)
    mode = models.CharField(max_length=20)
    private = models.IntegerField()
    event_active = models.IntegerField()
    approval = models.IntegerField()
    network_share = models.IntegerField()
    ticketing = models.IntegerField()
    promotion = models.IntegerField()
    connected_user = models.IntegerField()
    complete_details = models.IntegerField(blank=True, null=True)
    validation_status_sent = models.IntegerField(blank=True, null=True)
    leads_package = models.IntegerField(blank=True, null=True, default=0)
    step1_complete = models.IntegerField(blank=True, null=True, default=0)
    step2_complete = models.IntegerField(blank=True, null=True, default=0)
    step3_complete = models.IntegerField(blank=True, null=True, default=0)
    step4_complete = models.IntegerField(blank=True, null=True, default=0)
    step5_complete = models.IntegerField(blank=True, null=True, default=0)
    step6_complete = models.IntegerField(blank=True, null=True, default=0)
    sms_credit = models.IntegerField(blank=False, null=False, default=1000)
    email_credit = models.IntegerField(blank=False, null=False, default=1000)
    referrer_program_status = models.IntegerField(blank=False, null=False, default=1)
    affiliate = models.IntegerField(blank=False, null=False, default=0)

    class Meta:
        # managed = False
        db_table = 'status_promotion_ticketing'



class TicketAttendees(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    ticket_id = models.IntegerField()
    order_id = models.CharField(max_length=20)
    name = models.CharField(max_length=40)
    contact = models.CharField(max_length=10)
    email = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'ticket_attendees'


class TicketDiscounts(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    ticket_id = models.IntegerField()
    coupon = models.CharField(max_length=20)
    discount_amt = models.CharField(max_length=6)
    discount_type = models.IntegerField()
    discount_start = models.DateTimeField()
    discount_end = models.DateTimeField(blank=True, null=True)
    active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ticket_discounts'


class TicketOrdersErcess(models.Model):
    table_id = models.AutoField(primary_key=True)
    booking_id = models.CharField(max_length=40)
    txn_id = models.CharField(max_length=40)
    paid = models.IntegerField()
    event_id = models.IntegerField()
    total_amount = models.CharField(max_length=10)
    user_id = models.IntegerField()
    billing_name = models.CharField(max_length=50)
    billing_email = models.CharField(max_length=50)
    billing_phone = models.CharField(max_length=11)
    purchase_timestamp = models.DateTimeField()
    affiliate = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'ticket_orders_ercess'


class Tickets(models.Model):
    tickets_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    ticket_name = models.CharField(max_length=100)
    ticket_price = models.CharField(max_length=8)
    other_charges = models.CharField(max_length=6, blank=True, null=True)
    other_charges_type = models.IntegerField(blank=True, null=True)
    ticket_qty = models.IntegerField()
    min_qty = models.IntegerField()
    max_qty = models.IntegerField()
    qty_left = models.IntegerField()
    ticket_msg = models.CharField(max_length=200, blank=True, null=True)
    ticket_start_date = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateTimeField()
    ercess_fee = models.IntegerField()
    transaction_fee = models.IntegerField()
    ticket_label = models.CharField(max_length=20)
    active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tickets'

# @author Shubham
class TicketsSale(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField(null=False, default=0)
    ticket_id = models.IntegerField(null=False, default=0)
    booking_id = models.CharField(max_length=30, null=False, default='')
    oragnizer = models.IntegerField(null=False, default=0)
    ticket_type = models.CharField(max_length=100, null=False, default='')
    purchase_date = models.DateTimeField(null=False, default=datetime.now())
    ampunt_paid = models.FloatField(null=False, default=0)
    qty = models.IntegerField(null=False, default=1)
    attendee_name = models.CharField(max_length=30, null=False, default='')
    attendee_contact = models.CharField(max_length=12, null=False, default='')
    attendee_email = models.CharField(max_length=45, null=False, default='')
    seller_site = models.CharField(max_length=25, null=False, default='')
    ticket_handover = models.CharField(max_length=30, null=False, default='')

    class Meta:
        managed = False
        db_table = 'tickets_sale'

# ends here ~ @author Shubham

class TicketsSaleErcess(models.Model):
    cart_id = models.AutoField(primary_key=True)
    booking_id = models.CharField(max_length=40, null=False, default='')
    event_id = models.IntegerField(null=False, default=0)
    ticket_id = models.IntegerField(null=False, default=0)
    cart_timestamp = models.DateTimeField(null=False, default=datetime.now())
    qty = models.IntegerField(null=False, default=0)
    applied_coupon = models.CharField(null=False, max_length=10)
    coupon = models.CharField(max_length=10, default='', null=False)
    tickets_amount = models.FloatField(null=False, default=0)
    discounted_amount = models.CharField(max_length=10, null=False, default='0')
    extra_charges = models.FloatField(null=False, default=0)
    ercess_fees = models.CharField(max_length=10, null=False, default='0')
    processing_fee = models.CharField(max_length=10, null=False, default='0')
    cart_status = models.IntegerField(null=False, default=0)

    class Meta:
        managed = False
        db_table = 'tickets_sale_ercess'


class Topics(models.Model):
    topics_id = models.AutoField(primary_key=True)
    topic = models.CharField(max_length=50)
    category = models.CharField(max_length=37)

    class Meta:
        managed = False
        db_table = 'topics'


class Users(models.Model):
    social_userid = models.TextField(blank=True, null=True)
    md5 = models.CharField(max_length=36)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    user = models.CharField(max_length=40)
    profile_pic = models.TextField()
    gender = models.CharField(max_length=8)
    location = models.CharField(max_length=25)
    mobile = models.CharField(max_length=11)
    password = models.CharField(max_length=300, blank=True, null=True)
    mobile_verified = models.IntegerField()
    status = models.CharField(max_length=8)
    first_time = models.CharField(max_length=20)
    organization_name = models.CharField(max_length=200)
    organization_location = models.TextField()

    class Meta:
        # managed = False
        db_table = 'users'


class Users2(models.Model):
    social_userid = models.TextField(blank=True, null=True)
    md5 = models.CharField(max_length=36)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    user = models.CharField(max_length=40)
    profile_pic = models.TextField()
    gender = models.CharField(max_length=8)
    location = models.CharField(max_length=25)
    mobile = models.CharField(max_length=11)
    password = models.CharField(max_length=300, blank=True, null=True)
    mobile_verified = models.IntegerField()
    status = models.CharField(max_length=8)
    first_time = models.CharField(max_length=20)
    organization_name = models.CharField(max_length=200)
    organization_location = models.TextField()

    class Meta:
        managed = False
        db_table = 'users2'

# @author Shubham ~ leads model
class Leads(models.Model):
    name = models.CharField(max_length=50, null=False, default='')
    email = models.CharField(max_length=60, null=False, default='')
    contact = models.CharField(max_length=12, null=False, default='')
    city = models.CharField(max_length=30, null=False, default='')
    category = models.IntegerField(null=False, default='')
    sub_category = models.IntegerField(null=False, default='')
    user_id = models.IntegerField(null=False, default='')
    date_added = models.DateTimeField(null=False, default=timezone.now())

    class Meta:
        managed = False
        db_table = 'leads'


# ends here ~ @author Shubham  ~ leads model

# @author Shubham
class PackageSales(models.Model):
    table_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=False,default=0)
    purchase_date = models.DateTimeField(default=datetime.now(),null=False)
    booking_id = models.CharField(max_length=50,default='',null=False)
    price_paid = models.CharField(max_length=11,default='',null=False)
    package_bought = models.IntegerField(default=0,null=False)
    invoice_number = models.IntegerField(default=0,null=False)

    class Meta:
        managed = False
        db_table = 'package_sales'

class Announcements(models.Model):
    ann_id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=300, default='',null=False)
    mail_body = models.CharField(max_length=600, default='',null=False)
    dashboard_msg = models.CharField(max_length=600, default='',null=False)
    created_on = models.DateTimeField(default=datetime.now(),null=False)
    updated_on = models.DateTimeField(default=datetime.now(),null=False)
    status = models.CharField(max_length=30, default='deactive',null=False)

    class Meta:
        managed = False
        db_table = 'announcements'

class AnnouncementsAccess(models.Model):
    table_id = models.AutoField(primary_key=True)
    announcement_id = models.CharField(max_length=300, default='')
    user_id = models.CharField(max_length=600, default='')
    timestamp = models.DateTimeField(default=datetime.now())

    class Meta:
        managed = False
        db_table = 'announcements_access'

# @author Shubham
class ReferrerCashbackInfo(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.CharField(max_length=20, default='',null=False)
    payment_platform = models.CharField(max_length=50, default='',null=False)
    email_id = models.CharField(max_length=100,null=False,default='')
    referrer_code = models.CharField(max_length=30,null=False)
    code_generated_on = models.DateTimeField(default=datetime.now())
    # payable_amount = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'referrer_cashback_info'

class TicketSalesReference(models.Model):
    table_id = models.AutoField(primary_key=True)
    booking_id = models.CharField(max_length=20, default='',null=False)
    event_id = models.IntegerField(default=0)
    used_referred_code = models.CharField(max_length=30,null=False)
    cashback_to_process = models.IntegerField(default=0)
    cashback_process_status = models.CharField(max_length=30, default='',null=False)

    class Meta:
        managed = False
        db_table = 'ticket_sales_reference'

class ReferrerCashbackTokens(models.Model):
    id = models.AutoField(primary_key=True)
    token_code = models.CharField(max_length=100)
    attendee_email_id = models.CharField(max_length=100, default='')
    ticket_sales_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'referrer_cashback_tokens'

class ErcessOffers(models.Model):
    table_id = models.AutoField(primary_key=True)
    admin_id = models.IntegerField()
    date_added = models.DateTimeField(default=datetime.now())
    country = models.IntegerField()
    coupon_name = models.CharField(max_length=20)
    price_range_min = models.IntegerField()
    price_range_max = models.IntegerField()
    cashback = models.IntegerField()
    discount_amt = models.IntegerField()
    status = models.CharField(max_length=30, default='active')

    class Meta:
        managed = False
        db_table = 'ercess_offers'

# ends here ~ @author Shubham

# @author Shubham
class ShortUrlTracker(models.Model):
    id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    short_url = models.CharField(max_length=20)
    original_url = models.CharField(max_length=150)
    source = models.CharField(max_length=150)
    class Meta:
        managed = False
        db_table = 'short_url_tracker'
# ends here ~ @author Shubham

# @author Shubham
class CampaignTemplates(models.Model):
    template_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField(null=False)
    user_id = models.IntegerField(null=False)
    predefined_template_id = models.IntegerField(null=False, default=0)
    template_type = models.CharField(max_length=50)
    template_subject = models.CharField(max_length=100, null=False, default='')
    template_image = models.CharField(max_length=300, null=False, default='')
    template_msg = models.CharField(max_length=160, default='')
    template_link = models.CharField(max_length=4000, default='')
    is_standard = models.IntegerField(default=0)
    status = models.CharField(max_length=30, default='active')
    created_on = models.DateTimeField(default=datetime.now())
    scheduled_on = models.DateTimeField(default=datetime.now())
    class Meta:
        managed = False
        db_table = 'campaign_templates'
# ends here ~ @author Shubham

# @author Shubham
class CampaignStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    campaign_id = models.IntegerField()
    contact = models.CharField(max_length=50)
    contact_type = models.CharField(max_length=20)
    created_on = models.DateTimeField(default=datetime.now())
    updated_on = models.DateTimeField(default=datetime.now())
    status = models.CharField(max_length=30, default='scheduled')
    class Meta:
        managed = False
        db_table = 'campaign_status'
# ends here ~ @author Shubham

class ExpectationsFeedbacks(models.Model):
    expectations_feedbacks_id = models.AutoField(primary_key=True,)
    event_id = models.IntegerField()
    booking_id = models.CharField(default='',max_length=50)
    # booking_id = models.IntegerField(default=0)
    email = models.EmailField(max_length=50,default="email not provide")
    expectation_msg = models.TextField(max_length=500,null=True)
    uploaded_by = models.IntegerField(default=0)
    exp_email_attempts = models.IntegerField(default=0)
    exp_mail_status = models.CharField(max_length=20,default="pending")
    exp_timestamp = models.DateTimeField(auto_now_add=True)
    feedback_rating = models.IntegerField(default=0)
    feedback_msg = models.TextField(max_length=500,null=True)
    feedback_mail_attempts = models.IntegerField(default=0)
    feedback_timestamp = models.DateTimeField(auto_now_add=True)
    feedback_mail_status = models.CharField(max_length=20,default="pending")
    provided_for = models.CharField(max_length=50,default="expectation_and_feedback")
    class Meta:
        # managed = False
        db_table = 'expectations_feedbacks'

class CategoriesStalls(models.Model):
    table_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.category

    class Meta:
        managed = False
        db_table = 'categories_stalls'


class StallAudience(models.Model):
    table_id = models.AutoField(primary_key=True)
    audience_type = models.CharField(max_length=50)

    def __str__(self):
        return self.audience_type

    class Meta:
        managed = False
        db_table = 'stall_audience'


class StallFacilities(models.Model):
    power_backup = models.BooleanField()
    parking_space = models.BooleanField()
    water_supply = models.BooleanField()
    electricity = models.BooleanField()
    wifi = models.BooleanField()
    security = models.BooleanField()
    description = models.TextField()
    terms_and_condition = models.TextField()
    accepted_product = models.ManyToManyField(CategoriesStalls, related_name='products', null=True)
    expected_footfall = models.IntegerField()
    type_of_audience = models.ManyToManyField(StallAudience, related_name='audiences', null=True)
    event_id = models.IntegerField()

    def __str__(self):
        return str(self.event_id)


class StallUpload(models.Model):
    img = models.ImageField()
    file = models.FileField()
    event_id = models.IntegerField()


class Stall(models.Model):
    stall_name = models.CharField(max_length=254)
    total_quantity = models.IntegerField()
    booking_start_date = models.DateField(null=True)
    booking_start_time = models.TimeField(null=True)
    booking_end_date = models.DateField(null=True)
    booking_end_time = models.TimeField(null=True)
    full_stall_price = models.DecimalField(decimal_places=3, max_digits=20)
    half_stall_price = models.DecimalField(decimal_places=3, max_digits=20)
    number_of_chairs = models.IntegerField()
    counter = models.BooleanField(default=True)
    any_condition = models.TextField(max_length=300)
    size_in_meters = models.CharField(max_length=255)
    event_id = models.IntegerField()

    def __str__(self):
        return self.stall_name


class StallsProducts(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    stall_id = models.IntegerField()
    product_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'stalls_products'


class StallsAudience(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    stall_id = models.IntegerField()
    audience = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'stalls_audience'