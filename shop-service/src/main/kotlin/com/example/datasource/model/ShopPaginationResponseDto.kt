package com.example.datasource.model

import kotlinx.serialization.Serializable

@Serializable
data class ShopPaginationResponseDto(
    val page: Int,
    val pageSize: Int,
    val totalElements: Int,
    val items: List<ShopResponseDto>
)