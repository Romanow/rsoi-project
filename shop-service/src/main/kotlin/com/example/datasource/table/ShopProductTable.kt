package com.example.datasource.table

import org.jetbrains.exposed.sql.Column
import org.jetbrains.exposed.sql.ReferenceOption
import org.jetbrains.exposed.sql.Table

object ShopProductTable : Table() {
    val productId: Column<Int> = integer("product_id").references(ProductTable.id, onDelete = ReferenceOption.CASCADE)
    val shopId: Column<Int> = integer("shop_id").references(ShopTable.id, onDelete = ReferenceOption.CASCADE)
    val availableCount: Column<Int> = integer("available_count")
}