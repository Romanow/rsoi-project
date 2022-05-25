package com.example.domain.service

import com.example.domain.model.ProductData
import com.example.domain.model.SmallProductData
import java.util.*

interface IProductService {
    fun createProduct(productData: ProductData): Int
    fun getProduct(id: Int): ProductData
    fun getAllProducts(): List<ProductData>
    fun deleteProduct(id: Int)
    fun getProduct(uuid: UUID): SmallProductData
}