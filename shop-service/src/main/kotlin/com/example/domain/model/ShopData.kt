package com.example.domain.model

import java.util.*

data class ShopData(
    val id: Int? = null,
    val uuid: UUID,
    val name: String,
    val city: String,
    val address: String
)