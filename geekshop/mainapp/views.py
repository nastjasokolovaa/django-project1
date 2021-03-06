import random
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from mainapp.context_processors import get_links, get_links_menu, get_category_menu
from mainapp.models import ProductCategory, Product
from django.views.decorators.cache import cache_page


def get_products():
    return Product.objects


def get_hot_product():
    products = get_products().all()
    return random.sample(list(products), 1)[0]


def get_same_products(hot_products):
    same_products = get_products().filter(category=hot_products.category).exclude(pk=hot_products.pk)[:3]
    return same_products


# @cache_page(3600)
def products(request, pk=None, page=1):
    title = 'продукты'
    hot_product = get_hot_product()
    same_products = get_same_products(hot_product)
    links_menu = get_links_menu(request=request, title=title)
    if pk is not None:
        if pk == 0:
            products = get_products().all().order_by('price')
            category = {'name': 'все', 'pk': '0'}
        else:
            category = get_object_or_404(ProductCategory, pk=pk)
            products = get_products().filter(category_id__pk=pk).order_by('price')

        paginator = Paginator(products, 2)

        try:
            products_paginator = paginator.page(page)
        except PageNotAnInteger:
            products_paginator = paginator.page(1)
        except EmptyPage:
            products_paginator = paginator.page(1)

        links_menu.update(
            {
                'category': category,
                'products': products_paginator,
            }
        )
        return render(request, 'products_list.html', context=links_menu)
    else:
        links_menu.update(
            {
                'hot_product': hot_product,
                'same_products': same_products,
            }
        )
        return render(request, 'products.html', context=links_menu)


@login_required
def product(request, pk):
    title = 'Страница продукта'
    pk_product = get_object_or_404(Product, pk=pk)
    same_products = get_same_products(pk_product)
    category = ProductCategory.objects.filter(is_active=True)
    links_menu = {
        'links': list(get_links()),
        'auth': [{'href': 'auth:edit', 'name': 'пользователь'}],
        'categories': get_category_menu(),
        # 'categories': category,
        'title': title,
        'pk_product': pk_product,
        'same_products': same_products,
    }

    return render(request, 'product.html', context=links_menu)
