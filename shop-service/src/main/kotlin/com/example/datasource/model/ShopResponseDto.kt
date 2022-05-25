package com.example.datasource.model

import kotlinx.serialization.Serializable

@Serializable
data class ShopResponseDto(
    val uuid: String,
    val name: String,
    val city: String,
    val address: String
)