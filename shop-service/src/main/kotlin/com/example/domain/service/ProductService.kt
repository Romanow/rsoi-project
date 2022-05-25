package com.example.domain.service

import com.example.domain.model.ProductData
import com.example.domain.model.SmallProductData
import com.example.domain.repository.IProductRepository
import io.ktor.features.*
import java.util.*

class ProductService(
    private val productRepository: IProductRepository
): IProductService {
    override fun createProduct(productData: ProductData): Int =
        productRepository.createProduct(productData)

    override fun getProduct(id: Int): ProductData =
        productRepository.getProduct(id) ?: throw NotFoundException("Not found book")

    override fun getProduct(uuid: UUID): SmallProductData =
        productRepository.getProduct(uuid) ?: throw NotFoundException("Not found book")

    override fun getAllProducts(): List<ProductData> =
        productRepository.getAllProducts()

    override fun deleteProduct(id: Int) {
        productRepository.deleteProduct(id)
    }
}