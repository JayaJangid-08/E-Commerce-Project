from django.utils.timezone import now
from Discount.models import Discount


def build_items_from_cart(cart_items):
    # Converts cart items -> unified format for pricing engine
    items = []
    
    for item in cart_items:
        items.append({
            "product_id": item.product.id,
            "vendor_id": item.product.vendor_id,
            "price": item.product.price,
            "quantity": item.quantity
        })

    return items


def get_eligible_items(items, discount):
    eligible = []

    for item in items:
        if discount.applicable_to == 'all':
            eligible.append(item)

        elif discount.applicable_to == 'vendor':
            if discount.vendor_id and item['vendor_id'] == discount.vendor_id:
                eligible.append(item)

        elif discount.applicable_to == 'product':
            if discount.product_id and item['product_id'] == discount.product_id:
                eligible.append(item)

    return eligible


def calculate_discount(eligible_total, discount):
    if discount.discount_type == 'fixed':
        value = min(discount.discount_amount, eligible_total)
    else:
        value = (eligible_total * discount.discount_amount) / 100

        if discount.maximum_discount_amount:
            value = min(value, discount.maximum_discount_amount)

    return value


def apply_pricing(cart_items, coupon_name=None):
    subtotal = sum(i["price"] * i["quantity"] for i in cart_items)
    shipping = 100
    discount_amount = 0
    coupon = None

    if coupon_name:
        try:
            coupon = Discount.objects.get(coupon_name=coupon_name)
        except Discount.DoesNotExist:
            return {"error": "Invalid coupon"}

        if not coupon.is_active:
            return {"error": "Coupon inactive"}

        if coupon.expiry_date < now():
            return {"error": "Coupon expired"}
        
        if coupon.used_count >= coupon.usage_limit:
            return {"error": "Coupon usage limit reached"}
        
        eligible_items = get_eligible_items(cart_items, coupon)
        if not eligible_items:
            return {"error": "Coupon not applicable to any items"}
        
        eligible_total = sum(i["price"] * i["quantity"] for i in eligible_items)
        if eligible_total < coupon.minimum_order_amount:
            return {"error": f"Minimum order amount Rs. {coupon.minimum_order_amount} not met"}

        discount_amount = calculate_discount(eligible_total, coupon)

    final_price = max(subtotal + shipping - discount_amount, 0)

    return {
        "coupon": coupon_name,
        "coupon_obj": coupon,
        "subtotal": subtotal,
        "shipping_charge": shipping,
        "discount_amount": discount_amount,
        "final_price": final_price
    }

