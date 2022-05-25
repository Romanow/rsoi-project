package com.example.datasource.model

import kotlinx.serialization.Serializable

@Serializable
data class ErrorResponseDto(
    val message: String?
)
