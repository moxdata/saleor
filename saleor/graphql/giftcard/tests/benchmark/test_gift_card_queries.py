import graphene
import pytest

from ....tests.utils import get_graphql_content

FRAGMENT_EVENTS = """
    fragment GiftCardEvents on GiftCardEvent {
        id
        date
        type
        user {
            email
        }
        app {
            name
        }
        message
        email
        orderId
        orderNumber
        tag
        oldTag
        balance {
            initialBalance {
                amount
                currency
            }
            oldInitialBalance {
                amount
                currency
            }
            currentBalance {
                amount
                currency
            }
            oldCurrentBalance {
                amount
                currency
            }
        }
        expiry {
            expiryType
            oldExpiryType
            expiryPeriod {
                type
                amount
            }
            oldExpiryPeriod {
                type
                amount
            }
            expiryDate
            oldExpiryDate
        }
    }
"""

FRAGMENT_GIFT_CARD_DETAILS = (
    FRAGMENT_EVENTS
    + """
        fragment GiftCardDetails on GiftCard {
            id
            code
            displayCode
            isActive
            expiryDate
            expiryType
            expiryPeriod {
                amount
                type
            }
            tag
            created
            lastUsedOn
            initialBalance {
                currency
                amount
            }
            currentBalance {
                currency
                amount
            }
            createdBy {
                email
            }
            usedBy {
                email
            }
            createdByEmail
            usedByEmail
            app {
                name
            }
            product {
                name
            }
            events {
                ...GiftCardEvents
            }
        }
    """
)


@pytest.mark.django_db
@pytest.mark.count_queries(autouse=False)
def test_query_gift_card_details(
    staff_api_client,
    gift_card,
    gift_card_event,
    permission_manage_gift_card,
    permission_manage_users,
    permission_manage_apps,
    count_queries,
):
    query = (
        FRAGMENT_GIFT_CARD_DETAILS
        + """
        query giftCard($id: ID!) {
            giftCard(id: $id){
                ...GiftCardDetails
            }
        }
    """
    )
    variables = {
        "id": graphene.Node.to_global_id("GiftCard", gift_card.pk),
    }
    content = get_graphql_content(
        staff_api_client.post_graphql(
            query,
            variables,
            permissions=[
                permission_manage_gift_card,
                permission_manage_users,
                permission_manage_apps,
            ],
        )
    )

    assert content["data"]


@pytest.mark.django_db
@pytest.mark.count_queries(autouse=False)
def test_query_gift_cards(
    staff_api_client,
    gift_cards_for_benchmarks,
    permission_manage_gift_card,
    permission_manage_apps,
    permission_manage_users,
    count_queries,
):
    query = (
        FRAGMENT_GIFT_CARD_DETAILS
        + """
        query {
            giftCards(first: 20){
                edges {
                    node {
                        ...GiftCardDetails
                    }
                }
            }
        }
    """
    )
    content = get_graphql_content(
        staff_api_client.post_graphql(
            query,
            {},
            permissions=[
                permission_manage_gift_card,
                permission_manage_apps,
                permission_manage_users,
            ],
        )
    )

    assert content["data"]
    assert len(content["data"]["giftCards"]["edges"]) == len(gift_cards_for_benchmarks)