from logging import getLogger
log = getLogger("checkout.receivers")

from django.db.models import get_model
from django.contrib.sites.models import get_current_site
from django.contrib.auth.models import User

from oscar.core.loading import get_class

Dispatcher = get_class('customer.utils', 'Dispatcher')
CommunicationEventType = get_model('customer', 'CommunicationEventType')
advice_type_code = 'NEW_ORDER_ADVICE'
payment_received_code = 'PAYMENT_RECEIVED'
online_payment_codes = ('robokassa',)

def send_advice_message(sender, **kwargs):
    """ send advice message about new order to manager """
    log.info(80*'=')
    log.info('Sending advice message')
    log.info(80*'=')

    code = advice_type_code
    order = kwargs['order']
    user = kwargs['user']
    ctx = {'user': user,
            'order': order,
            'lines': order.lines.all()}
    try:
        event_type = CommunicationEventType.objects.get(code=code)
    except CommunicationEventType.DoesNotExist:
        # No event-type in database, attempt to find templates for this
        # type and render them immediately to get the messages.  Since we
        # have not CommunicationEventType to link to, we can't create a
        # CommunicationEvent instance.
        messages = CommunicationEventType.objects.get_and_render(code, ctx)
        event_type = None
    else:
        messages = event_type.get_messages(ctx)

    if messages and messages['body']:
        for manager in User.objects.filter(is_staff=True):  # Here we should pick users from managers group
            if manager.email:
                dispatcher = Dispatcher()
                try:
                    dispatcher.dispatch_direct_messages(
                        manager.email, messages)
                except:
                    log.warning("Advice message send failed")


def send_payment_received(sender, **kwargs):
    """ send thank you for your payment """
    log.info(80*'=')
    log.info('Sending payment received message')
    log.info(80*'=')
    email = None
    site = None
    code = payment_received_code
    user = kwargs.get('user', None)
    source = kwargs.get('source', None)
    source_type = None
    if hasattr(sender, 'request'):
        request = sender.request
        site = get_current_site(request)
    if user is None or not user.is_authenticated():
        if hasattr(sender, 'checkout_session'):
            email = sender.checkout_session.get_guest_email()
    else:
        email = user.email

    if email is None:
        return

    amount_debited = 0
    if source is None and hasattr(sender, '_payment_sources'):
        for s in sender._payment_sources:
            amount_debited += s.amount_debited
        if hasattr(sender, 'checkout_session'):
            source_type = sender.checkout_session.payment_method()

    else:
        amount_debited = source.amount_debited
        source_type = source.source_type

    if amount_debited == 0 or source_type is None or source_type.code \
            not in online_payment_codes:
        return

    ctx = {'user': user,
            'site': site,
            'amount_debited': amount_debited,
            'source_type': source_type}

    try:
        event_type = CommunicationEventType.objects.get(code=code)
    except CommunicationEventType.DoesNotExist:
        # No event-type in database, attempt to find templates for this
        # type and render them immediately to get the messages.  Since we
        # have not CommunicationEventType to link to, we can't create a
        # CommunicationEvent instance.
        messages = CommunicationEventType.objects.get_and_render(code, ctx)
        event_type = None
    else:
        messages = event_type.get_messages(ctx)

    if messages and messages['body']:
        dispatcher = Dispatcher()
        try:
            dispatcher.dispatch_direct_messages(email, messages)
        except:
            log.warning("Payment received send failed")

def send_order_placed(sender, **kwargs):
    if 'confirmation_not_sent' in kwargs:
        log.info("Sending confirmation with no session restored")
        if 'order' in kwargs:
            try:
                sender.send_confirmation_message(kwargs['order'])
            except:
                log.warning("Order #%s - no confirmation was sent",
                            kwargs['order'].number)
