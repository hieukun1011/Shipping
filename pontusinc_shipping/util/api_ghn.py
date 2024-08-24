# URL UAT API VNPOST
URL = 'https://dev-online-gateway.ghn.vn'

#API get all shop
get_shop = '/shiip/public-api/v2/shop/all'

# GET Province
get_province = '/shiip/public-api/master-data/province'

# GET district
get_district = '/shiip/public-api/master-data/district'

# GET ward
get_ward = '/shiip/public-api/master-data/ward'

# POST order
post_order = '/shiip/public-api/v2/shipping-order/create'

# GET service
# Use this API to get service packages by route.
get_service = '/shiip/public-api/v2/shipping-order/available-services'

# Create shop
create_shop = '/shiip/public-api/v2/shop/register'

# Use this API to calculate service fees before creating an order via GHN.
fee_shipping = '/shiip/public-api/v2/shipping-order/fee'

# Use this API to redeliver orders when they are in the process of being returned.
return_order = '/shiip/public-api/v2/switch-status/storing'

# get token print shipping waybill
get_token = '/shiip/public-api/v2/a5/gen-token'

# print shipping waybill
print_waybill = '/a5/public-api/printA5'

# Use this API to return items when the sender wants to cancel the delivery.
switch_status_return = '/shiip/public-api/v2/switch-status/return'

