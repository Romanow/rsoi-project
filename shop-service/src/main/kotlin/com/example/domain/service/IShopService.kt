package com.example.domain.service

import com.example.domain.model.ShopData
import java.util.*

interface IShopService {
    fun createShop(shopData: ShopData): Int
    fun getShop(id: Int): ShopData
    fun getAllShops(): List<ShopData>
    fun deleteShop(id: Int)
    fun getShop(uuid: UUID): ShopData
    fun getShops(page: Int, size: Int, city: String): List<ShopData>
}