package com.example.domain.repository

import com.example.domain.model.ProductData
import com.example.domain.model.ShopProductData
import java.util.*

interface IShopProductRepository {
    fun createShopProduct(shopProductData: ShopProductData)
    fun getProductsInShop(limit: Int, offset: Long, showAll: Boolean, shopUuid: UUID): List<ProductData>
    fun updateAvailableCount(shopUuid: UUID, bookUuid: UUID, increase: Boolean)
}