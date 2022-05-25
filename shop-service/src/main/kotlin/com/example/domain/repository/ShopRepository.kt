package com.example.domain.repository

import com.example.datasource.mapper.toShopData
import com.example.datasource.table.ShopTable
import com.example.domain.model.ShopData
import org.jetbrains.exposed.sql.deleteWhere
import org.jetbrains.exposed.sql.insert
import org.jetbrains.exposed.sql.select
import org.jetbrains.exposed.sql.selectAll
import java.util.*

class ShopRepository : IShopRepository {
    override fun createShop(shopData: ShopData): Int {
        return ShopTable.insert {
            shopData.id?.let { sId-> it[id] = sId }
            it[uuid] = shopData.uuid
            it[name] = shopData.name
            it[city] = shopData.city
            it[address] = shopData.address
        }[ShopTable.id]
    }

    override fun deleteShop(id: Int) {
        ShopTable.deleteWhere {
            ShopTable.id eq id
        }
    }

    override fun updateShop(id: Int, shopData: ShopData): ShopData? {
        TODO("Not yet implemented")
    }

    override fun getShop(id: Int): ShopData? {
        val shop = ShopTable.select {
            ShopTable.id eq id
        }.singleOrNull() ?: return null

        return shop.toShopData()
    }

    override fun getShop(uuid: UUID): ShopData? {
        val shop = ShopTable.select {
            ShopTable.uuid eq uuid
        }.singleOrNull() ?: return null

        return shop.toShopData()
    }

    override fun getAllShops(): List<ShopData> {
        val shopList = mutableListOf<ShopData>()
        ShopTable.selectAll().map {
            shopList.add(it.toShopData())
        }
        return shopList
    }

    override fun getShops(limit: Int, offset: Long, city: String): List<ShopData> {
        val shopList = mutableListOf<ShopData>()
        ShopTable.select {
            ShopTable.city eq city
        }.limit(limit, offset).map {
            shopList.add(it.toShopData())
        }

        return shopList
    }
}