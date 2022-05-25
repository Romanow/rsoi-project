package com.example.domain.model

import java.util.*

data class ProductData(
    val id: Int? = null,
    val uuid: UUID,
    val name: String,
    val description: String?,
    val price: Long,
    val availableCount: Int? = null
)