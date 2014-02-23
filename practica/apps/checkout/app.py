from oscar.apps.checkout import app
from oscar.core.loading import get_classes

from apps.checkout import views

class CheckoutApplication(app.CheckoutApplication):
    payment_method_view = views.PaymentMethodView
    payment_details_view = views.PaymentDetailsView
    thankyou_view = views.ThankYouView


application = CheckoutApplication()

from apps.checkout.receivers import send_advice_message,\
        send_payment_received, send_order_placed
post_payment, post_checkout = get_classes('checkout.signals',
                            ['post_payment', 'post_checkout'])

post_checkout.connect(send_advice_message)
post_checkout.connect(send_order_placed)
post_payment.connect(send_payment_received)
