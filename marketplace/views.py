from django.shortcuts import render

from marketplace.models import Product


def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {'product': product}
    return render(request, 'marketplace/product_detail.html', context)
