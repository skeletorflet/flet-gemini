import 'package:flet/flet.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gemini/flutter_gemini.dart';
import 'dart:convert';
import 'dart:typed_data';
import 'dart:async';

class FletGeminiControl extends StatefulWidget {
  final Control? parent;
  final Control control;
  final List<Control> children;
  final bool parentDisabled;
  final bool? parentAdaptive;
  final FletControlBackend backend;

  const FletGeminiControl({
    super.key,
    required this.parent,
    required this.control,
    required this.children,
    required this.parentDisabled,
    required this.parentAdaptive,
    required this.backend,
  });

  @override
  State<FletGeminiControl> createState() => _FletGeminiControlState();
}

class _FletGeminiControlState extends State<FletGeminiControl> {
  String _response = "";
  bool _isLoading = false;
  String? _error;
  StreamSubscription? _streamSubscription;

  // Configuration state
  GenerationConfig? _generationConfig;
  List<SafetySetting>? _safetySettings;
  String? _systemPrompt;

  @override
  void initState() {
    super.initState();
    widget.backend.subscribeMethods(widget.control.id, _onMethodCall);

    // Initialize Gemini if API key is provided
    final String? apiKey = widget.control.attrString("api_key", null);
    if (apiKey != null && apiKey.isNotEmpty) {
      _initializeGemini(apiKey);
    }

    // Load configuration
    _loadConfiguration();
  }

  @override
  void dispose() {
    widget.backend.unsubscribeMethods(widget.control.id);
    _streamSubscription?.cancel();
    super.dispose();
  }

  Future<String?> _onMethodCall(
      String methodName, Map<String, String> args) async {
    switch (methodName) {
      case "prompt":
        return await _handlePrompt(args["text"] ?? "", args["model"]);
      case "init":
        return await _handleInit(args["api_key"] ?? "");
      case "chat":
        return await _handleChat(args);
      case "stream_chat":
        return await _handleStreamChat(args);
      case "count_tokens":
        return await _handleCountTokens(args);
      case "info":
        return await _handleInfo(args);
      case "list_models":
        return await _handleListModels();
      case "embed_content":
        return await _handleEmbedContent(args);
      case "batch_embed_contents":
        return await _handleBatchEmbedContents(args);
      case "cancel_request":
        return await _handleCancelRequest();
      case "text_and_image":
        return await _handleTextAndImage(args);
      default:
        return null;
    }
  }

  void _initializeGemini(String apiKey) {
    try {
      Gemini.init(
        apiKey: apiKey,
        enableDebugging: true,
        safetySettings: _safetySettings,
        generationConfig: _generationConfig,
      );
    } catch (e) {
      _triggerError("Error initializing Gemini: $e");
    }
  }

  void _loadConfiguration() {
    // Load generation config
    final String? genConfigJson =
        widget.control.attrString("generation_config", null);
    if (genConfigJson != null) {
      try {
        final Map<String, dynamic> config = json.decode(genConfigJson);
        _generationConfig = GenerationConfig(
          temperature: config['temperature']?.toDouble(),
          topK: config['topK']?.toInt(),
          topP: config['topP']?.toDouble(),
          maxOutputTokens: config['maxOutputTokens']?.toInt(),
          stopSequences: config['stopSequences']?.cast<String>(),
        );
      } catch (e) {
        // Invalid config, use defaults
      }
    }
    // Load safety settings
    final String? safetyJson =
        widget.control.attrString("safety_settings", null);
    if (safetyJson != null) {
      try {
        final List<dynamic> settings = json.decode(safetyJson);
        _safetySettings = settings
            .map((s) => SafetySetting(
                  category: SafetyCategory.values.firstWhere(
                    (c) => c.name == s['category'],
                    orElse: () => SafetyCategory.harassment,
                  ),
                  threshold: SafetyThreshold.values.firstWhere(
                    (t) => t.name == s['threshold'],
                    orElse: () => SafetyThreshold.blockMediumAndAbove,
                  ),
                ))
            .toList();
      } catch (e) {
        // Invalid settings, use defaults
      }
    }

    // Load system prompt
    _systemPrompt = widget.control.attrString("system_prompt", null);
  }

  Future<String?> _handleInit(String apiKey) async {
    try {
      _initializeGemini(apiKey);
      return "Gemini initialized successfully";
    } catch (e) {
      return "Error initializing Gemini: $e";
    }
  }

  Future<String?> _handlePrompt(String text, String? model) async {
    if (text.isEmpty) return "Error: Empty prompt";

    try {
      final response = await Gemini.instance.prompt(
        parts: [Part.text(text)],
        model: model,
        safetySettings: _safetySettings,
        generationConfig: _generationConfig,
      );

      final output = response?.output ?? "No response";
      _triggerResponse(output);
      return output;
    } catch (e) {
      final errorMsg = "Error: $e";
      _triggerError(errorMsg);
      return errorMsg;
    }
  }

  Future<String?> _handleChat(Map<String, String> args) async {
    try {
      final String? chatsJson = args["chats"];
      if (chatsJson == null) return "Error: No chats provided";

      final List<dynamic> chatsData = json.decode(chatsJson);
      final List<Content> chats = chatsData
          .map((chat) => Content(
                role: chat['role'] ?? 'user',
                parts: (chat['parts'] as List)
                    .map((part) => Part.text(part['text'] ?? ''))
                    .toList(),
              ))
          .toList();

      final response = await Gemini.instance.chat(
        chats,
        modelName: args["model"],
        safetySettings: _safetySettings,
        generationConfig: _generationConfig,
        systemPrompt: _systemPrompt,
      );

      final output = response?.output ?? "No response";
      _triggerChatResponse(output);
      return output;
    } catch (e) {
      final errorMsg = "Error in chat: $e";
      _triggerError(errorMsg);
      return errorMsg;
    }
  }

  Future<String?> _handleStreamChat(Map<String, String> args) async {
    try {
      final String? chatsJson = args["chats"];
      if (chatsJson == null) return "Error: No chats provided";

      final List<dynamic> chatsData = json.decode(chatsJson);
      final List<Content> chats = chatsData
          .map((chat) => Content(
                role: chat['role'] ?? 'user',
                parts: (chat['parts'] as List)
                    .map((part) => Part.text(part['text'] ?? ''))
                    .toList(),
              ))
          .toList();

      _streamSubscription?.cancel();
      _streamSubscription = Gemini.instance
          .streamChat(
        chats,
        modelName: args["model"],
        safetySettings: _safetySettings,
        generationConfig: _generationConfig,
      )
          .listen(
        (response) {
          final chunk = response.output ?? "";
          _triggerChunk(chunk);
        },
        onError: (error) {
          _triggerError("Stream error: $error");
        },
      );

      return "Stream started";
    } catch (e) {
      final errorMsg = "Error starting stream: $e";
      _triggerError(errorMsg);
      return errorMsg;
    }
  }

  Future<String?> _handleCountTokens(Map<String, String> args) async {
    try {
      final String? text = args["text"];
      if (text == null) return "Error: No text provided";

      final count = await Gemini.instance.countTokens(
        text,
        modelName: args["model"],
        // safetySettings: _safetySettings,
        // generationConfig: _generationConfig,
      );

      return count?.toString() ?? "0";
    } catch (e) {
      final errorMsg = "Error counting tokens: $e";
      _triggerError(errorMsg);
      return errorMsg;
    }
  }

  Future<String> _handleInfo(Map<String, String> args) async {
    try {
      final String? model = args["model"];
      if (model == null) return json.encode({"error": "No model specified"});

      final info = await Gemini.instance.info(model: model);
      return json.encode(info.toJson());
    } catch (e) {
      final errorMsg = {"error": "Error getting model info: $e"};
      _triggerError(errorMsg.toString());
      return json.encode(errorMsg);
    }
  }

  Future<String> _handleListModels() async {
    try {
      final models = await Gemini.instance.listModels();
      final modelList = models.map((m) => m.toJson()).toList();
      return json.encode(modelList);
    } catch (e) {
      final errorMsg = {"error": "Error listing models: $e"};
      _triggerError(errorMsg.toString());
      return json.encode(errorMsg);
    }
  }

  Future<String> _handleEmbedContent(Map<String, String> args) async {
    try {
      final String? text = args["text"];
      if (text == null) return json.encode({"error": "No text provided"});

      print("Processing text: '$text'");

      // NO uses safetySettings ni generationConfig para embeddings
      final embedding = await Gemini.instance.embedContent(
        text,
        modelName: args["model"] ?? "embedding-001",
      );

      print("Embedding result: $embedding");

      if (embedding == null) {
        return json.encode({"error": "No embedding returned"});
      }

      final result = json.encode({"embedding": embedding});
      print("Final JSON: $result");

      return result;
    } catch (e) {
      print("Exception in _handleEmbedContent: $e");
      final errorMsg = {"error": "Error embedding content: $e"};
      return json.encode(errorMsg);
    }
  }

  Future<String> _handleBatchEmbedContents(Map<String, String> args) async {
    try {
      final String? textsJson = args["texts"];
      if (textsJson == null) return json.encode({"error": "No texts provided"});

      final List<String> texts = List<String>.from(json.decode(textsJson));

      final embeddings = await Gemini.instance.batchEmbedContents(
        texts,
        modelName: args["model"] ?? "embedding-001",
        // safetySettings: _safetySettings,
        // generationConfig: _generationConfig,
      );

      if (embeddings == null) {
        return json.encode({"error": "No embeddings returned"});
      }

      // Cambio: mantienes el formato de array de arrays
      return json
          .encode({"embeddings": embeddings.map((e) => e ?? []).toList()});
    } catch (e) {
      final errorMsg = {"error": "Error batch embedding: $e"};
      _triggerError(errorMsg.toString());
      return json.encode(errorMsg);
    }
  }

  Future<String?> _handleCancelRequest() async {
    try {
      await Gemini.instance.cancelRequest();
      _streamSubscription?.cancel();
      return "Request cancelled";
    } catch (e) {
      final errorMsg = "Error cancelling request: $e";
      _triggerError(errorMsg);
      return errorMsg;
    }
  }

  Future<String?> _handleTextAndImage(Map<String, String> args) async {
    try {
      final String? text = args["text"];
      final String? imagesJson = args["images"];

      if (text == null || imagesJson == null) {
        return "Error: Text and images required";
      }

      final List<dynamic> imageData = json.decode(imagesJson);
      final List<Uint8List> images = imageData
          .map((img) => Uint8List.fromList(List<int>.from(img)))
          .toList();

      // Crear las partes para el prompt
      List<Part> parts = [Part.text(text)];

      // Agregar cada imagen como Part.bytes
      for (Uint8List imageBytes in images) {
        parts.add(Part.bytes(imageBytes));
      }

      // Usar prompt en lugar de textAndImage
      final response = await Gemini.instance.prompt(
        parts: parts,
        model: args["model"],
        safetySettings: _safetySettings,
        generationConfig: _generationConfig,
      );

      // Usar response?.output como en el ejemplo que funciona
      final output = response?.output ?? "No response";
      _triggerResponse(output);
      return output;
    } catch (e) {
      final errorMsg = "Error with text and image: $e";
      _triggerError(errorMsg);
      return errorMsg;
    }
  }

  void _triggerResponse(String response) {
    var props = {"response": response};
    widget.backend.updateControlState(widget.control.id, props);
    widget.backend
        .triggerControlEvent(widget.control.id, "on_response", response);
  }

  void _triggerChatResponse(String response) {
    var props = {"response": response};
    widget.backend.updateControlState(widget.control.id, props);
    widget.backend
        .triggerControlEvent(widget.control.id, "on_chat_response", response);
  }

  void _triggerChunk(String chunk) {
    widget.backend.triggerControlEvent(widget.control.id, "on_chunk", chunk);
  }

  void _triggerError(String error) {
    widget.backend.triggerControlEvent(widget.control.id, "on_error", error);
  }

  @override
  Widget build(BuildContext context) {
    // Auto-prompt if prompt is provided and not already processed
    String prompt = widget.control.attrString("prompt", "") ?? "";
    if (prompt.isNotEmpty &&
        _response.isEmpty &&
        !_isLoading &&
        _error == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _handlePrompt(prompt, widget.control.attrString("model", null));
      });
    }

    // Return an empty, non-visual widget
    return baseControl(
        context, const SizedBox.shrink(), widget.parent, widget.control);
  }
}
