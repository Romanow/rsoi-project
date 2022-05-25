package com.example.datasource.model

import kotlinx.serialization.Serializable

@Serializable
data class ProductPaginationResponseDto(
    val page: Int,
    val pageSize: Int,
    val totalElements: Int,
    val items: List<ProductResponseDto>
)