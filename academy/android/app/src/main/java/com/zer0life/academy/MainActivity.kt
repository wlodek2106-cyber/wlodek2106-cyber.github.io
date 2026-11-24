package com.zer0life.academy
import android.os.Bundle
import android.content.Intent
import android.net.Uri
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.*
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.glance.appwidget.updateAll
import kotlinx.coroutines.*
import org.json.JSONObject
import java.net.URL
import javax.net.ssl.HttpsURLConnection
class MainActivity : ComponentActivity() {
    private var token: String? = null
    private suspend fun request(path: String, body: JSONObject? = null): JSONObject = withContext(Dispatchers.IO) {
        val c = URL("https://zer0life-academy.onrender.com/"+path).openConnection() as HttpsURLConnection
        try {
            c.instanceFollowRedirects = false
            c.connectTimeout = 20000
            c.readTimeout = 20000
            token?.let { c.setRequestProperty("Authorization","Bearer "+it) }
            if(body != null) {
                c.requestMethod = "POST"
                c.doOutput = true
                c.setRequestProperty("Content-Type","application/json")
                c.outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
            }
            check(c.responseCode in 200..299)
            JSONObject(c.inputStream.bufferedReader().use { it.readText() })
        } finally { c.disconnect() }
    }
    private suspend fun clearProgress() {
        getSharedPreferences("academy_progress", MODE_PRIVATE).edit().clear().apply()
        AcademyWidget().updateAll(this)
    }
    private suspend fun sync(): String {
        val p = request("progress")
        val lessons = p.getJSONArray("lessons")
        if(!p.getBoolean("paid") || lessons.length() !in listOf(30,40,45)) {
            clearProgress()
            return "No active paid course"
        }
        val n = (0 until lessons.length()).count { lessons.getJSONObject(it).getBoolean("completed") }
        getSharedPreferences("academy_progress", MODE_PRIVATE).edit().putInt("completed",n).putInt("total",lessons.length()).apply()
        AcademyWidget().updateAll(this)
        return "Widget synchronized"
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme(colorScheme = darkColorScheme()) {
            var email by remember { mutableStateOf("") }
            var password by remember { mutableStateOf("") }
            var signedIn by remember { mutableStateOf(false) }
            var busy by remember { mutableStateOf(false) }
            var status by remember { mutableStateOf("") }
            val scope = rememberCoroutineScope()
            Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.Center) {
                Text("ZER0LIFE Academy", style = MaterialTheme.typography.headlineLarge)
                if(!signedIn) {
                    OutlinedTextField(email,{email=it},label={Text("Email")},singleLine=true)
                    OutlinedTextField(password,{password=it},label={Text("Password")},visualTransformation=PasswordVisualTransformation(),singleLine=true)
                    Button(enabled=!busy && email.isNotBlank() && password.isNotEmpty(),onClick={
                        busy=true
                        scope.launch {
                            try {
                                clearProgress()
                                token=request("login",JSONObject().put("email",email).put("password",password)).getString("token")
                                status=sync()
                                signedIn=true
                            } catch(e: CancellationException) { throw e } catch(e: Exception) { token=null; status="Sign-in or sync failed" }
                            finally { password=""; busy=false }
                        }
                    }) { Text("Sign in & sync") }
                } else {
                    Button(enabled=!busy,onClick={busy=true;scope.launch {
                        try { status=sync() } catch(e: CancellationException){throw e} catch(e:Exception){clearProgress();status="Sync failed"} finally {busy=false}
                    }}) { Text("Refresh widget") }
                    Button(enabled=!busy,onClick={busy=true;scope.launch {
                        try { request("logout",JSONObject()) } catch(e:CancellationException){throw e} catch(e:Exception){} finally {token=null;signedIn=false;clearProgress();busy=false;status="Signed out"}
                    }}) { Text("Sign out") }
                }
                Button(onClick={startActivity(Intent(Intent.ACTION_VIEW,Uri.parse("https://zer0life-academy.onrender.com/dashboard")))}) {Text("Open Academy")}
                Text(status)
            }
        } }
    }
}
