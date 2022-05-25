package com.example.datasource.model

import kotlinx.serialization.Serializable

@Serializable
data class ProductResponseDto(
    val uuid: String,
    val name: String,
    val description: String?,
    val price: Long,
    val availableCount: Int
)