package com.example.chatrpg.ui

import com.example.chatrpg.R

fun getBackgroundForRegion(region: String): Int {
    return when (region) {
        "공허" -> R.drawable.void_bg
        "숲" -> R.drawable.forest_bg
        "도시" -> R.drawable.city_bg
        else -> R.drawable.city_bg
    }
}
