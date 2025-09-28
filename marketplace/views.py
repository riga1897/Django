from django.shortcuts import render

from marketplace.models import Product


def products_list(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "marketplace/products_list.html", context)

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {'product': product}
    return render(request, "marketplace/product_detail.html", context)
