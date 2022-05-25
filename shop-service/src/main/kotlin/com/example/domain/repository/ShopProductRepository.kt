package com.example.domain.repository

import com.example.datasource.mapper.toProductData
import com.example.datasource.table.ProductTable
import com.example.datasource.table.ShopProductTable
import com.example.datasource.table.ShopTable
import com.example.domain.model.ProductData
import com.example.domain.model.ShopProductData
import io.ktor.features.*
import org.jetbrains.exposed.sql.*
import java.util.*

class ShopProductRepository : IShopProductRepository {
    override fun createShopProduct(shopProductData: ShopProductData) {
        ShopProductTable.insert {
            it[productId] = shopProductData.productId
            it[shopId] = shopProductData.shopId
            it[availableCount] = shopProductData.availableCount
        }
    }

    override fun getProductsInShop(limit: Int, offset: Long, showAll: Boolean, shopUuid: UUID): List<ProductData> {
        val productList = mutableListOf<ProductData>()
        val products = ShopProductTable
            .join(ShopTable, JoinType.INNER, ShopProductTable.shopId, ShopTable.id) {
                ShopTable.uuid eq shopUuid
            }
            .join(ProductTable, JoinType.INNER, ShopProductTable.productId, ProductTable.id)

        val selectedProducts = if (showAll)
            products.selectAll()
        else
            products.select { ShopProductTable.availableCount neq 0 }
        selectedProducts
            .limit(limit, offset)
            .map {
                productList.add(it.toProductData())
            }

        return productList
    }

    override fun updateAvailableCount(shopUuid: UUID, bookUuid: UUID, increase: Boolean) {
        val shop = ShopTable.select { (ShopTable.uuid eq shopUuid) }.singleOrNull() ?: throw NotFoundException("Shop not found")
        val product = ProductTable.select { (ProductTable.uuid eq bookUuid) }.singleOrNull() ?: throw NotFoundException("Product not found")
        val shopProduct = ShopProductTable.select { ((ShopProductTable.shopId eq shop[ShopTable.id]) and (ShopProductTable.productId  eq product[ProductTable.id])) }.singleOrNull() ?: throw NotFoundException("Shop product not found")

        val currentAvailableCount = if (increase)
            shopProduct[ShopProductTable.availableCount] + 1
        else
            shopProduct[ShopProductTable.availableCount] - 1

        ShopProductTable.update({
            (ShopProductTable.shopId eq shop[ShopTable.id]) and (ShopProductTable.productId eq product[ProductTable.id])
        }) {
            it[availableCount] = currentAvailableCount
        }
    }
}