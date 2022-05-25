import org.gradle.api.tasks.testing.logging.TestExceptionFormat
import org.gradle.api.tasks.testing.logging.TestLogEvent.*
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

val ktorVersion: String by project
val kotlinVersion: String by project
val logbackVersion: String by project
val exposedVersion: String by project
val serializationVersion: String by project
val postgresVersion: String by project
val koinVersion: String by project
val mockitoVersion: String by project

plugins {
    application
    kotlin("jvm") version "1.5.31"
    kotlin("plugin.serialization") version "1.5.31"
    id("com.github.johnrengelman.shadow") version "4.0.4"
}

group = "com.example"
version = "1.0.0"
application {
    mainClassName = "com.example.ApplicationKt"
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:$serializationVersion")
    implementation("org.jetbrains.exposed:exposed-core:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-dao:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-jdbc:$exposedVersion")
    implementation("org.postgresql:postgresql:$postgresVersion")
    implementation("io.ktor:ktor-server-core:$ktorVersion")
    implementation("io.ktor:ktor-server-netty:$ktorVersion")
    implementation("io.ktor:ktor-serialization:$ktorVersion")
    implementation("ch.qos.logback:logback-classic:$logbackVersion")
    implementation("io.insert-koin:koin-core:$koinVersion")
    implementation("io.insert-koin:koin-ktor:$koinVersion")
    implementation("io.insert-koin:koin-logger-slf4j:$koinVersion")

    testImplementation("io.ktor:ktor-server-tests:$ktorVersion")
    testImplementation("io.insert-koin:koin-test:$koinVersion")
    testImplementation("io.insert-koin:koin-test-junit4:$koinVersion")
    testImplementation("org.jetbrains.kotlin:kotlin-test:$kotlinVersion")
    testImplementation("org.mockito:mockito-core:$mockitoVersion")
}

tasks.withType<KotlinCompile>().configureEach {
    kotlinOptions.jvmTarget = "1.8"
}

tasks.test {
    testLogging {
        events = setOf(FAILED, PASSED, SKIPPED, STANDARD_OUT)
        exceptionFormat = TestExceptionFormat.FULL
        showExceptions = true
        showCauses = true
        showStackTraces = true

        debug {
            events = setOf(STARTED, FAILED, PASSED, SKIPPED, STANDARD_ERROR, STANDARD_OUT)
            exceptionFormat = TestExceptionFormat.FULL
        }
        info{
            events = debug.events
            exceptionFormat = debug.exceptionFormat
        }
    }
    addTestListener(object : TestListener {
        override fun beforeTest(p0: TestDescriptor?) = Unit
        override fun beforeSuite(p0: TestDescriptor?) = Unit
        override fun afterTest(desc: TestDescriptor, result: TestResult) = Unit
        override fun afterSuite(desc: TestDescriptor, result: TestResult) {
            printResults(desc, result)
        }
    })
}

fun printResults(desc: TestDescriptor, result: TestResult) {
    if (desc.parent != null) {
        val output = result.run {
            "Results: $resultType (" +
                    "$testCount tests, " +
                    "$successfulTestCount successes, " +
                    "$failedTestCount failures, " +
                    "$skippedTestCount skipped" +
                    ")"
        }
        val testResultLine = "|  $output  |"
        val repeatLength = testResultLine.length
        val separationLine = "-".repeat(repeatLength)
        println(separationLine)
        println(testResultLine)
        println(separationLine)
    }
}