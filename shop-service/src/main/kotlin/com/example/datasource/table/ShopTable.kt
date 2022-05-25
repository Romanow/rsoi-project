package com.example.datasource.table

import org.jetbrains.exposed.sql.Column
import org.jetbrains.exposed.sql.Table
import java.util.*

object ShopTable : Table() {
    val id: Column<Int> = integer("id").autoIncrement()
    val uuid: Column<UUID> = uuid("shop_uuid")
    val name: Column<String> = varchar("name", 80)
    val city: Column<String> = varchar("city", 255)
    val address: Column<String> = varchar("address", 255)

    override val primaryKey = PrimaryKey(id, name = "PK_SHOP_ID")
}