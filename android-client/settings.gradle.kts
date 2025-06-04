pluginManagement {
    repositories {
        google()
        gradlePluginPortal()
    }
    plugins {
        // Kotlin Compose Plugin 명시
        id("org.jetbrains.kotlin.plugin.compose") version "1.5.11"
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "ChatRPG"
include(":app")
