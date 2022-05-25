package com.example.datasource.table

import org.jetbrains.exposed.sql.Column
import org.jetbrains.exposed.sql.Table
import java.util.*

object ProductTable : Table() {
    val id: Column<Int> = integer("id").autoIncrement()
    val uuid: Column<UUID> = uuid("book_uuid")
    val name: Column<String> = varchar("name", 255)
    val description: Column<String?> = varchar("description", 255).nullable()
    val price: Column<Long> = long("price")

    override val primaryKey = PrimaryKey(id, name = "PK_PRODUCT_ID")
}