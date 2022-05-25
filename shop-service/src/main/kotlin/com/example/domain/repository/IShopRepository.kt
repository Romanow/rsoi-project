package com.example.domain.repository

import com.example.domain.model.ShopData
import java.util.*

interface IShopRepository {
    fun createShop(shopData: ShopData): Int
    fun deleteShop(id: Int)
    fun updateShop(id:Int, shopData: ShopData): ShopData?
    fun getShop(id: Int): ShopData?
    fun getAllShops(): List<ShopData>
    fun getShop(uuid: UUID): ShopData?
    fun getShops(limit: Int, offset: Long, city: String): List<ShopData>
}