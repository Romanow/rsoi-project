package com.example

import com.example.di.repositoryModule
import com.example.di.serviceModule
import com.example.domain.model.*
import com.example.domain.repository.IShopProductRepository
import com.example.domain.service.IShopProductService
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

class ShopProductTest : KoinTest {
    private val shopProductService: IShopProductService by inject()

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
    private val availableCount = 1
    private val productData =  ProductData(
        id,
        uuid,
        name,
        description,
        price,
        availableCount
    )

    @Test
    fun `Create Shop Product`() {
        val shopProductData = ShopProductData(1, 1, 1)
        declareMock<IShopProductRepository> {
        }
        shopProductService.createShopProduct(shopProductData)
    }

    @Test
    fun `Get Products in Shop`() {
        val page = 1
        val size = 0
        val expectedSize = 1
        val showAll = false
        val limit = 0
        val offset = 0L

        declareMock<IShopProductRepository> {
            given(getProductsInShop(limit, offset, showAll, uuid)).willReturn(mutableListOf(productData))
        }

        val realProductDataList = shopProductService.getProductsInShop(page, size, showAll, uuid)
        assertEquals(expectedSize, realProductDataList.size)
    }

    @Test
    fun `Update available count`() {
        declareMock<IShopProductRepository> {
        }
        shopProductService.updateAvailableCount(uuid,  uuid, false)
    }
}