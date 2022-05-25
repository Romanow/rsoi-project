package com.example.domain.repository

import com.example.domain.model.ProductData
import com.example.domain.model.SmallProductData
import java.util.*

interface IProductRepository {
    fun createProduct(productData: ProductData): Int
    fun updateProduct(id: Int, productData: ProductData): ProductData?
    fun deleteProduct(id: Int)
    fun getProduct(id: Int): ProductData?
    fun getAllProducts(): List<ProductData>
    fun getProduct(uuid: UUID): SmallProductData?
}