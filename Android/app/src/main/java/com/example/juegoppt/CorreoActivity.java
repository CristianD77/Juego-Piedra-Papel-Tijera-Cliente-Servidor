package com.example.juegoppt;

import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.Scanner;

public class CorreoActivity extends AppCompatActivity {

    // =============================================
    // CONFIGURACION
    // =============================================
    private static final String IP_SERVIDOR = "192.168.20.8";
    private static final int    PUERTO      = 1234;

    // =============================================
    // VARIABLES
    // =============================================
    private Socket      socket;
    private PrintWriter salida;
    private Scanner     entrada;
    private boolean     conectado = false;

    private EditText etCorreo;
    private TextView tvEstadoCorreo;
    private Button   btnEnviarCorreo, btnVolverMenu;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_correo);

        etCorreo       = findViewById(R.id.etCorreo);
        tvEstadoCorreo = findViewById(R.id.tvEstadoCorreo);
        btnEnviarCorreo = findViewById(R.id.btnEnviarCorreo);
        btnVolverMenu  = findViewById(R.id.btnVolverMenu);

        // Conectar al servidor
        new Thread(() -> conectar()).start();

        // Enviar correo
        btnEnviarCorreo.setOnClickListener(v -> {
            String correo = etCorreo.getText().toString().trim();
            if (correo.isEmpty()) {
                mostrarAlerta("Aviso", "Ingresa un correo.");
                return;
            }
            tvEstadoCorreo.setText("Enviando...");
            enviarMensaje("CORREO|" + correo);
        });

        // Volver al menú
        btnVolverMenu.setOnClickListener(v -> {
            enviarMensaje("cerrar");
            cerrarConexion();
            finish();
        });
    }

    // =============================================
    // CONEXION
    // =============================================
    private void conectar() {
        try {
            socket    = new Socket(IP_SERVIDOR, PUERTO);
            salida    = new PrintWriter(socket.getOutputStream(), true);
            entrada   = new Scanner(socket.getInputStream());
            conectado = true;

            // Avisar al servidor que es cliente de consulta
            salida.println("SOLO_CORREO");

            runOnUiThread(() ->
                    tvEstadoCorreo.setText("Conectado. Ingresa tu correo.")
            );

            // Escuchar respuestas
            while (conectado && entrada.hasNextLine()) {
                String mensaje = entrada.nextLine();
                procesarRespuesta(mensaje);
            }
        } catch (Exception e) {
            runOnUiThread(() ->
                    mostrarAlerta("Error", "No se pudo conectar al servidor.")
            );
        }
    }

    // =============================================
    // PROCESAR RESPUESTAS
    // =============================================
    private void procesarRespuesta(String texto) {
        String[] partes  = texto.split("\\|");
        String   comando = partes[0];

        runOnUiThread(() -> {
            switch (comando) {
                case "LISTO_CORREO":
                    tvEstadoCorreo.setText("Conectado. Ingresa tu correo.");
                    break;

                case "CORREO_OK":
                    tvEstadoCorreo.setText("Resultados enviados exitosamente.");
                    mostrarAlerta("Correo", "Resultados enviados exitosamente.");
                    break;

                case "CORREO_ERROR":
                    tvEstadoCorreo.setText("Error al enviar el correo.");
                    mostrarAlerta("Error", "No se pudo enviar el correo.");
                    break;
            }
        });
    }

    // =============================================
    // FUNCIONES AUXILIARES
    // =============================================
    private void enviarMensaje(String mensaje) {
        new Thread(() -> {
            if (salida != null) {
                salida.println(mensaje);
            }
        }).start();
    }

    private void cerrarConexion() {
        try {
            conectado = false;
            if (socket != null) socket.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void mostrarAlerta(String titulo, String mensaje) {
        runOnUiThread(() ->
                new AlertDialog.Builder(CorreoActivity.this)
                        .setTitle(titulo)
                        .setMessage(mensaje)
                        .setPositiveButton("OK", null)
                        .show()
        );
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        enviarMensaje("cerrar");
        cerrarConexion();
    }
}