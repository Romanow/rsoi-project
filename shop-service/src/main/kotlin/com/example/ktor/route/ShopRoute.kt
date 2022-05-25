package com.example.ktor.route

import com.example.datasource.mapper.toProductResponseDto
import com.example.datasource.mapper.toShopResponseDto
import com.example.datasource.mapper.toSmallProductDto
import com.example.datasource.model.ProductPaginationResponseDto
import com.example.datasource.model.ShopPaginationResponseDto
import com.example.domain.service.IProductService
import com.example.domain.service.IShopProductService
import com.example.domain.service.IShopService
import io.ktor.application.*
import io.ktor.http.*
import io.ktor.response.*
import io.ktor.routing.*
import org.jetbrains.exposed.sql.transactions.transaction
import org.koin.ktor.ext.inject
import java.util.*

fun Route.getShopsRoute() {
    val shopService: IShopService by inject()
    get("shops") {
        val page = call.request.queryParameters["page"]?.toInt() ?: 0
        val size = call.request.queryParameters["size"]?.toInt() ?: 1
        val city = call.request.queryParameters["city"] ?: return@get

        val shops = transaction {
            shopService.getShops(page, size, city)
        }

        val shopResponseDto = ShopPaginationResponseDto(
            page, size, shops.size, shops.map { it.toShopResponseDto() }
        )

        call.response.status(HttpStatusCode.OK)
        call.respond(shopResponseDto)
    }
}

fun Route.getShopRoute() {
    val shopService: IShopService by inject()
    get("shops/{shopUuid}") {
        val shopUuid = call.parameters["shopUuid"] ?: return@get
        val shop = transaction {
            shopService.getShop(UUID.fromString(shopUuid))
        }.toShopResponseDto()
        call.response.status(HttpStatusCode.OK)
        call.respond(shop)
    }
}

fun Route.getProductRoute() {
    val productService: IProductService by inject()
    get("products/{productUuid}") {
        val productUuid = call.parameters["productUuid"] ?: return@get

        val product = transaction {
            productService.getProduct(UUID.fromString(productUuid))
        }.toSmallProductDto()

        call.response.status(HttpStatusCode.OK)
        call.respond(product)

    }
}

fun Route.getProductsInShopRoute() {
    val shopProductService: IShopProductService by inject()
    get("shops/{shopUuid}/books") {
        val page = call.request.queryParameters["page"]?.toInt() ?: 0
        val size = call.request.queryParameters["size"]?.toInt() ?: 1
        val showAll = call.request.queryParameters["showAll"]?.toBoolean() ?: false
        val shopUuid = call.parameters["shopUuid"] ?: return@get

        val products = transaction {
            shopProductService.getProductsInShop(page, size, showAll, UUID.fromString(shopUuid))
        }
        val productPaginationDto = ProductPaginationResponseDto(
            page, size, products.size, products.map { it.toProductResponseDto() }
        )
        call.response.status(HttpStatusCode.OK)
        call.respond(productPaginationDto)
    }
}

fun Route.updateAvailableCount() {
    val shopProductService: IShopProductService by inject()
    post("shops/{shopUuid}/products/{productUuid}") {
        val increase = call.request.queryParameters["increase"]?.toBoolean() ?: false
        val shopUuid = call.parameters["shopUuid"] ?: return@post
        val productUuid = call.parameters["productUuid"] ?: return@post

        transaction {
            shopProductService.updateAvailableCount(
                UUID.fromString(shopUuid),
                UUID.fromString(productUuid),
                increase
            )
        }
        call.response.status(HttpStatusCode.OK)
        call.respondText("")
    }
}
