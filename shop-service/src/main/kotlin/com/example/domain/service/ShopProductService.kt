package com.example.domain.service

import com.example.domain.model.ProductData
import com.example.domain.model.ShopProductData
import com.example.domain.repository.IShopProductRepository
import java.util.*

class ShopProductService(
    private val shopProductRepository: IShopProductRepository
) : IShopProductService{
    override fun createShopProduct(shopProductData: ShopProductData) {
        shopProductRepository.createShopProduct(shopProductData)
    }

    override fun getProductsInShop(page: Int, size: Int, showAll: Boolean, libraryUUID: UUID): List<ProductData> =
        shopProductRepository.getProductsInShop(size, (page - 1) * size.toLong(), showAll, libraryUUID)

    override fun updateAvailableCount(shopUuid: UUID, productUuid: UUID, increase: Boolean) {
        shopProductRepository.updateAvailableCount(shopUuid, productUuid, increase)
    }
}