package com.example.di

import com.example.domain.repository.*
import org.koin.dsl.module

val repositoryModule = module {
    single<IShopRepository> { ShopRepository() }
    single<IProductRepository> { ProductRepository() }
    single<IShopProductRepository> { ShopProductRepository() }
}