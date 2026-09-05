package com.pulse.ai.companion

import java.net.HttpURLConnection
import java.net.URL
import org.json.JSONObject

/**
 * HTTP Client forwarding Android notifications securely to PULSE AI Backend API.
 */
class PulseApiClient {

    private val backendUrl = "https://pulse-ai-backend.onrender.com/api/v1/mobile/notifications"

    fun sendNotification(sourceApp: String, title: String, content: String): Boolean {
        try {
            val url = URL(backendUrl)
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json; utf-8")
            conn.doOutput = true

            val jsonPayload = JSONObject().apply {
                put("source_app", sourceApp)
                put("title", title)
                put("content", content)
            }

            conn.outputStream.use { os ->
                val input = jsonPayload.toString().toByteArray(Charsets.UTF_8)
                os.write(input, 0, input.size)
            }

            val responseCode = conn.responseCode
            return responseCode == 200 || responseCode == 201
        } catch (e: Exception) {
            e.printStackTrace()
            return false
        }
    }
}
