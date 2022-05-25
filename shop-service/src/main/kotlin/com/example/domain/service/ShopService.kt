package com.example.domain.service

import com.example.domain.model.ShopData
import com.example.domain.repository.IShopRepository
import io.ktor.features.*
import java.util.*

class ShopService(
    private val shopRepository: IShopRepository
) : IShopService {
    override fun createShop(shopData: ShopData): Int =
        shopRepository.createShop(shopData)

    override fun getShop(id: Int): ShopData =
        shopRepository.getShop(id) ?: throw NotFoundException("Library not found")

    override fun getShop(uuid: UUID): ShopData =
        shopRepository.getShop(uuid) ?: throw NotFoundException("Library not found")

    override fun getAllShops(): List<ShopData> =
        shopRepository.getAllShops()

    override fun deleteShop(id: Int) {
        shopRepository.deleteShop(id)
    }

    override fun getShops(page: Int, size: Int, city: String): List<ShopData> =
       shopRepository.getShops(size,  (page - 1) * size.toLong(), city)
}