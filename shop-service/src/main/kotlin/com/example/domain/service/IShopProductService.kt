package com.example.domain.service

import com.example.domain.model.ProductData
import com.example.domain.model.ShopProductData
import java.util.*

interface IShopProductService {
    fun createShopProduct(shopProductData: ShopProductData)
    fun getProductsInShop(page: Int, size: Int, showAll: Boolean, libraryUUID: UUID): List<ProductData>
    fun updateAvailableCount(shopUuid: UUID, productUuid: UUID, increase: Boolean)
}