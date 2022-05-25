package com.example.datasource.model

import kotlinx.serialization.Serializable

@Serializable
data class SmallProductResponseDto(
    val uuid: String,
    val name: String,
    val description: String?,
)
