package com.example.di

import com.example.domain.service.*
import org.koin.dsl.module

val serviceModule = module {
    single<IProductService> { ProductService(get()) }
    single<IShopService> { ShopService(get()) }
    single<IShopProductService> { ShopProductService(get()) }
}