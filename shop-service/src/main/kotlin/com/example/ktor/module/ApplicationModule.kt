package com.example.ktor.module

import com.example.datasource.model.ErrorResponseDto
import com.example.datasource.table.ProductTable
import com.example.datasource.table.ShopProductTable
import com.example.datasource.table.ShopTable
import com.example.di.repositoryModule
import com.example.di.serviceModule
import com.example.ktor.route.*
import io.ktor.application.*
import io.ktor.features.*
import io.ktor.http.*
import io.ktor.response.*
import io.ktor.routing.*
import io.ktor.serialization.*
import kotlinx.serialization.json.Json
import org.jetbrains.exposed.sql.Database
import org.jetbrains.exposed.sql.SchemaUtils
import org.jetbrains.exposed.sql.StdOutSqlLogger
import org.jetbrains.exposed.sql.addLogger
import org.jetbrains.exposed.sql.transactions.transaction
import org.koin.ktor.ext.Koin
import org.koin.logger.SLF4JLogger

fun Application.main() {
    connectToDataBase()
    installKtorFeatures()
}

fun Application.routing() {
    routing {
        getShopsRoute()
        getProductsInShopRoute()
        updateAvailableCount()
        getShopRoute()
        getProductRoute()
    }
}

private fun Application.installKtorFeatures() {
    install(StatusPages) {
        exception<NotFoundException> {
            call.response.status(HttpStatusCode.NotFound)
            call.respond(ErrorResponseDto(it.message))
        }
    }

    install(DefaultHeaders)
    install(CallLogging)
    install(ContentNegotiation) {
        json(Json {
            prettyPrint = true
            isLenient = true
        })
    }
    install(Koin) {
        SLF4JLogger()
        modules(repositoryModule, serviceModule)
    }
}

private const val url = "jdbc:postgresql://ec2-18-202-67-49.eu-west-1.compute.amazonaws.com:5432/d698988au6kgin"
private const val user = "hinttpijkhvcxy"
private const val password = "2ab06602895307adfd33613c0295d3edba138952462f466d08ac46b9f78227e6"

private fun connectToDataBase() {
    Database.connect(url, user = user, password = password)
    transaction {
        addLogger(StdOutSqlLogger)
        SchemaUtils.create(ProductTable, ShopTable, ShopProductTable)
    }
}
