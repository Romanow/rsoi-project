package com.example

import com.example.di.repositoryModule
import com.example.di.serviceModule
import com.example.domain.model.ShopData
import com.example.domain.repository.IShopRepository
import com.example.domain.service.IShopService
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

class ShopTest : KoinTest {
    private val shopService: IShopService by inject()

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(repositoryModule, serviceModule)
    }

    @get:Rule
    val mockProvider = MockProviderRule.create { clazz ->
        Mockito.mock(clazz.java)
    }

    private val name = "kek"
    private val city  = "kek"
    private val uuid: UUID = UUID.fromString("0d3b8de1-30d6-45c5-95ec-81c550362312")
    private val address = "kek"
    private val id = 1
    private val shopData = ShopData(
        id,
        uuid,
        name,
        city,
        address
    )

    @Test
    fun `Create shop`() {

        declareMock<IShopRepository> {
            given(createShop(shopData)).willReturn(id)
        }

        val realId = shopService.createShop(shopData)
        assertEquals(id, realId)
    }

    @Test
    fun `Get shop by uuid`() {
        declareMock<IShopRepository> {
            given(getShop(uuid)).willReturn(shopData)
        }

        val realShopData = shopService.getShop(uuid)
        assertShopData(shopData, realShopData)
    }

    @Test(expected = NotFoundException::class)
    fun `Get shop by uuid not found`() {
        declareMock<IShopRepository> {
            given(getShop(uuid)).willReturn(null)
        }

        shopService.getShop(uuid)
    }

    @Test
    fun `Get Shop by id`() {
        declareMock<IShopRepository> {
            given(getShop(id)).willReturn(shopData)
        }

        val realShopData = shopService.getShop(id)
        assertShopData(shopData, realShopData)
    }

    @Test(expected = NotFoundException::class)
    fun `Get shop by id not found`() {
        declareMock<IShopRepository> {
            given(getShop(id)).willReturn(null)
        }

        shopService.getShop(id)
    }

    @Test
    fun `Get all shops`() {
        val expectedSize = 1
        declareMock<IShopRepository> {
            given(getAllShops()).willReturn(mutableListOf(shopData))
        }

        val realShopDataList = shopService.getAllShops()
        assertEquals(realShopDataList.size, expectedSize)
    }

    @Test
    fun `Delete shop`() {
        declareMock<IShopRepository> {
        }
        shopService.deleteShop(id)
    }

    @Test
    fun `Get shops`() {
        val page = 1
        val size = 0
        val expectedSize = 1
        val limit = 0
        val offset = 0L

        declareMock<IShopRepository> {
            given(getShops(limit, offset, city)).willReturn(mutableListOf(shopData))
        }
        val realShopDataList = shopService.getShops(page, size, city)
        assertEquals(expectedSize, realShopDataList.size)
    }

    private fun assertShopData(s1: ShopData, s2: ShopData) {
        assertEquals(s1.id, s2.id)
        assertEquals(s1.address, s2.address)
        assertEquals(s1.city, s2.city)
        assertEquals(s1.uuid, s2.uuid)
        assertEquals(s1.name, s2.name)
    }
}