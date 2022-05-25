package com.example

import com.example.di.repositoryModule
import com.example.di.serviceModule
import com.example.domain.model.ProductData
import com.example.domain.model.SmallProductData
import com.example.domain.repository.IProductRepository
import com.example.domain.service.IProductService
import io.ktor.features.*
import org.junit.Rule
import org.junit.Test
import org.koin.test.KoinTest
import org.koin.test.KoinTestRule
import org.koin.test.inject
import org.koin.test.mock.MockProviderRule
import org.koin.test.mock.declareMock
import org.mockito.BDDMockito.given
import org.mockito.Mockito
import java.util.*
import kotlin.test.assertEquals

class ProductTest : KoinTest {
    private val productService: IProductService by inject()

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(repositoryModule, serviceModule)
    }

    @get:Rule
    val mockProvider = MockProviderRule.create { clazz ->
        Mockito.mock(clazz.java)
    }

    private val name = "kek"
    private val description  = "kek"
    private val uuid: UUID = UUID.fromString("0d3b8de1-30d6-45c5-95ec-81c550362312")
    private val id = 1
    private val price = 100L
    private val productData =  ProductData(
        id,
        uuid,
        name,
        description,
        price,
        null
    )
    private val smallProductData = SmallProductData(
        uuid,
        name,
        description
    )

    @Test
    fun `Create product`() {

        declareMock<IProductRepository> {
            given(createProduct(productData)).willReturn(id)
        }

        val realId = productService.createProduct(productData)
        assertEquals(id, realId)
    }

    @Test
    fun `Get product by uuid`() {
        declareMock<IProductRepository> {
            given(getProduct(uuid)).willReturn(smallProductData)
        }

        val realSmallProductData = productService.getProduct(uuid)
        assertSmallProductData(smallProductData, realSmallProductData)
    }

    @Test(expected = NotFoundException::class)
    fun `Get product by uuid not found`() {
        declareMock<IProductRepository> {
            given(getProduct(uuid)).willReturn(null)
        }

        productService.getProduct(uuid)
    }

    @Test
    fun `Get product by id`() {
        declareMock<IProductRepository> {
            given(getProduct(id)).willReturn(productData)
        }

        val realProductData = productService.getProduct(id)
        assertProductData(productData, realProductData)
    }

    @Test(expected = NotFoundException::class)
    fun `Get product by id not found`() {
        declareMock<IProductRepository> {
            given(getProduct(id)).willReturn(null)
        }

        productService.getProduct(id)
    }

    @Test
    fun `Get all products`() {
        val expectedSize = 1
        declareMock<IProductRepository> {
            given(getAllProducts()).willReturn(mutableListOf(productData))
        }

        val realProductDataList = productService.getAllProducts()
        assertEquals(expectedSize, realProductDataList.size)
    }

    @Test
    fun `Delete product`() {
        declareMock<IProductRepository> {
        }
        productService.deleteProduct(id)
    }

    private fun assertProductData(p1: ProductData, p2: ProductData) {
        assertEquals(p1.id, p2.id)
        assertEquals(p1.description, p2.description)
        assertEquals(p1.availableCount, p2.availableCount)
        assertEquals(p1.uuid, p2.uuid)
        assertEquals(p1.name, p2.name)
        assertEquals(p1.price, p2.price)
    }

    private fun assertSmallProductData(p1: SmallProductData, p2: SmallProductData) {
        assertEquals(p1.name, p2.name)
        assertEquals(p1.uuid, p2.uuid)
        assertEquals(p1.description, p2.description)
    }
}