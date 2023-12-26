from yoomoney import Authorize, Quickpay
from src.config import Config

def yoomoney_authorize():
    return Authorize(
        client_id="",
        redirect_uri="",
        scope=["account-info",
               "operation-history",
               "operation-details",
               "incoming-transfers",
               "payment-p2p",
               "payment-shop"]
    )


def yoomoney_create_url(total_price, label):
    quickpay = Quickpay(
        receiver=Config.receiver,
        quickpay_form='shop',
        targets='',
        paymentType='',
        sum=total_price,
        label=label
    )
    url = quickpay.redirected_url

    return url
