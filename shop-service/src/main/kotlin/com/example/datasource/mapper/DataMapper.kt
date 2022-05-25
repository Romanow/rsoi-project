package com.example.datasource.mapper

import com.example.datasource.model.ProductResponseDto
import com.example.datasource.model.ShopResponseDto
import com.example.datasource.model.SmallProductResponseDto
import com.example.domain.model.ProductData
import com.example.domain.model.ShopData
import com.example.domain.model.SmallProductData
import java.util.*

fun ProductData.toProductResponseDto() = ProductResponseDto(
    uuid = uuid.toString(),
    name = name,
    description = description,
    price = price,
    availableCount = availableCount!!
)

fun ShopData.toShopResponseDto() = ShopResponseDto(
    uuid = uuid.toString(),
    name = name,
    city = city,
    address = address
)

fun SmallProductData.toSmallProductDto() = SmallProductResponseDto(
    uuid = uuid.toString(),
    name  = name,
    description = description
)

fun SmallProductResponseDto.toSmallProductData() = SmallProductData(
    uuid = UUID.fromString(uuid),
    name = name,
    description = description,
)