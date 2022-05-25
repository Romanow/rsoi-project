package com.example.domain.repository

import com.example.datasource.mapper.toProductData
import com.example.datasource.mapper.toProductWithoutIdData
import com.example.datasource.table.ProductTable
import com.example.domain.model.ProductData
import com.example.domain.model.SmallProductData
import org.jetbrains.exposed.sql.deleteWhere
import org.jetbrains.exposed.sql.insert
import org.jetbrains.exposed.sql.select
import org.jetbrains.exposed.sql.selectAll
import java.util.*

class ProductRepository : IProductRepository {
    override fun createProduct(productData: ProductData): Int {
        return ProductTable.insert {
            productData.id?.let { pId -> it[id] = pId }
            it[uuid] = productData.uuid
            it[name] = productData.name
            it[description] = productData.description
            it[price]
        }[ProductTable.id]
    }

    override fun updateProduct(id: Int, productData: ProductData): ProductData? {
        TODO("Not yet implemented")
    }

    override fun deleteProduct(id: Int) {
        ProductTable.deleteWhere {
            ProductTable.id eq id
        }
    }

    override fun getProduct(id: Int): ProductData? {
        val product = ProductTable.select {
            ProductTable.id eq id
        }.singleOrNull() ?: return null

        return product.toProductData()
    }

    override fun getProduct(uuid: UUID): SmallProductData? {
        val product = ProductTable.select {
            ProductTable.uuid eq uuid
        }.singleOrNull() ?: return null

        return product.toProductWithoutIdData()
    }

    override fun getAllProducts(): List<ProductData> {
        val productList = mutableListOf<ProductData>()
        ProductTable.selectAll().map {
            productList.add(it.toProductData())
        }
        return productList
    }
}