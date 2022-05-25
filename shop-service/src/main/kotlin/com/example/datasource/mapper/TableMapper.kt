package com.example.datasource.mapper

import com.example.datasource.table.ProductTable
import com.example.datasource.table.ShopProductTable
import com.example.datasource.table.ShopTable
import com.example.domain.model.ProductData
import com.example.domain.model.SmallProductData
import com.example.domain.model.ShopData
import org.jetbrains.exposed.sql.ResultRow

fun ResultRow.toProductData(): ProductData =
    ProductData(
        id = this[ProductTable.id],
        uuid = this[ProductTable.uuid],
        name = this[ProductTable.name],
        description = this[ProductTable.description],
        price = this[ProductTable.price],
        availableCount = this[ShopProductTable.availableCount]
    )

fun ResultRow.toProductWithoutIdData(): SmallProductData =
    SmallProductData(
        uuid = this[ProductTable.uuid],
        name = this[ProductTable.name],
        description = this[ProductTable.description]
    )

fun ResultRow.toShopData(): ShopData =
    ShopData(
        id = this[ShopTable.id],
        uuid = this[ShopTable.uuid],
        name = this[ShopTable.name],
        city = this[ShopTable.city],
        address = this[ShopTable.address]
    )